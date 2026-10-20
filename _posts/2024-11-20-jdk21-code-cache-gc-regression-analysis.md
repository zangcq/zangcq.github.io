---
title: JDK 21 升级后 GC 时间上涨：一次 Code Cache 回收问题的定位与分析
date: 2024-11-20
categories:
  - jvm
tags:
  - jdk21
  - code-cache
  - gc
  - g1
  - troubleshooting
  - performance
excerpt: 从 JDK 17 升级到 JDK 21 后 GC 累计时间上涨 60%+，根因一半在 Code Cache 回收策略过于激进，一半在 G1 MXBean 统计口径变化。
---

# JDK 21 升级后 GC 时间上涨：一次 Code Cache 回收问题的定位与分析

在一次从 JDK 17 升级到 JDK 21 的大数据基准测试中，我们观察到任务整体吞吐变化不算明显，但监控中的累计 GC 时间却上涨了 60% 以上。

这类问题很容易被直接归因于 G1 的性能退化，但进一步分析后发现，指标上涨其实由两部分共同造成：

1. **真实开销增加**：JDK 21 中 Code Cache 的回收机制发生变化，特定阈值逻辑会触发过于频繁的 GC。
2. **统计口径变化**：新版 JDK 将此前未计入 `GarbageCollectorMXBean` 的部分停顿纳入统计，使监控值天然高于旧版本。

本文记录完整的定位思路，并重点讨论 Code Cache、G1 与 GC 指标之间容易被忽略的关系。

## 一、先确认这是性能退化，还是指标变化

面对“GC 时间上涨”时，首先要区分三个概念：

- GC 事件是否变多；
- GC 停顿是否变长；
- 监控系统统计到的 GC 时间是否变大。

三者并不等价。累计 GC 时间通常来自类似下面的代码：

```scala
ManagementFactory.getGarbageCollectorMXBeans
  .asScala
  .map(_.getCollectionTime)
  .sum
```

这意味着监控结果依赖 JVM 如何维护 `GarbageCollectorMXBean`，而不仅仅取决于应用实际经历的停顿。

因此，排查时不能只比较监控面板上的总数，还需要同时检查：

- GC 日志中的事件类型和触发原因；
- 各类停顿的次数与耗时分布；
- JDK 不同版本之间 MXBean 的统计口径变化；
- 应用吞吐、任务执行时间和 CPU 使用率是否同步退化。

## 二、通过版本二分缩小范围

为了排除业务代码、数据规模和参数变化的干扰，可以在保持工作负载与 JVM 参数一致的前提下，对 JDK 大版本做二分验证。

测试结果将问题范围缩小到 JDK 19 与 JDK 20 之间：

- JDK 19 GA 未出现异常；
- JDK 20 GA 开始出现异常；
- JDK 21 延续了这一行为。

这一步非常关键。相比逐个尝试 GC 参数，版本二分能够快速把排查范围收敛到一组有限的 HotSpot 变更。

> 实际测试旧版 Hadoop 生态组件时，还要注意版本号解析兼容性。某些旧代码通过 `java.version.substring(0, 3)` 判断 Java 版本，无法正确处理 `20`、`21` 这类版本号，可能在 JVM 初始化前就抛出异常。此类兼容性问题与 GC 本身无关，应单独处理，避免干扰二分结果。

## 三、GC 日志暴露出的异常信号

对比升级前后的 GC 日志后，可以看到新版 JDK 中出现了大量类似事件：

```text
Pause Young (Concurrent Start) (CodeCache GC Threshold)
```

这说明并不是普通的分配压力或老年代占用触发了并发标记，而是 **Code Cache 达到某个回收阈值后主动请求 GC**。

Code Cache 用于存放 JIT 编译后的机器码、运行时 Stub 等内容。它不属于 Java Heap，但代码卸载需要与垃圾收集器协作：只有在确认对应类或方法不再存活后，JVM 才能安全回收相关 nmethod。

因此，Code Cache 压力可能间接触发堆 GC。升级后如果突然出现大量 `CodeCache GC Threshold`，就应重点检查代码缓存的分配速度、容量和回收触发逻辑，而不是只分析对象分配速率。

可用于辅助诊断的参数包括：

```text
-XX:+PrintCodeCache
-XX:+PrintCodeCacheOnCompilation
-Xlog:codecache*=debug,gc*=info
```

不同 JDK 版本支持的日志选项可能不同，使用前应通过 `java -Xlog:help` 或对应版本文档确认。

## 四、根因：移除 Sweeper 后的 Code Cache 回收策略

问题最终指向 OpenJDK 的 [JDK-8290025: Remove the Sweeper](https://github.com/openjdk/jdk21u/commit/054c23f484522881a0879176383d970a8de41201)。

传统 HotSpot 中，Code Cache 由 Sweeper 逐步清理失效的 nmethod。移除 Sweeper 后，代码卸载更多地与 GC 周期绑定；与此同时，Code Cache 在分配路径上会根据剩余容量和自上次卸载以来的增长量判断是否请求 GC。

其核心判断可以概括为：

```cpp
free_ratio = free / max;
allocated_ratio = (used - last_used) / max;
threshold = SweeperThreshold / 100.0;

if (used_ratio > threshold) {
    threshold *= free_ratio;
}

if (allocated_ratio > threshold) {
    request_code_cache_gc();
}
```

这里存在一个容易导致误判的放大效应：

1. Code Cache 使用率超过基础阈值后，触发阈值会再乘以 `free_ratio`；
2. 随着可用空间减少，`free_ratio` 下降；
3. 实际阈值随之进一步降低；
4. 即使 Code Cache 仍有较多空闲空间，较小的新增代码量也可能再次触发 GC。

如果每轮并发标记本身已经会执行代码卸载，那么分配路径继续高频请求卸载型 GC，收益有限，却会制造额外的并发周期与停顿。

这也解释了一个看似反常的现象：**扩大 Code Cache 容量只能降低触发频率，却不能从根本上修复不合理的触发策略。** 它适合作为验证手段或临时缓解措施，而不是最终结论。

## 五、修复验证应该看什么

调整 Code Cache 的 GC 触发逻辑后，验证不能只看单一的累计 GC 时间。建议至少比较以下指标：

1. `CodeCache GC Threshold` 触发次数；
2. G1 并发标记周期数量；
3. Young、Mixed、Remark、Cleanup 等停顿的次数和分位耗时；
4. `GarbageCollectorMXBean#getCollectionTime()` 的累计值；
5. 应用端到端执行时间与 CPU 消耗；
6. Code Cache 的峰值使用量和最终使用量。

修复后，Code Cache 触发的额外 GC 应显著减少，累计 GC 时间也会明显回落。不过，它未必完全回到 JDK 17 的水平，因为 JDK 20 之后还存在统计口径变化。

## 六、为什么修复后 GC 时间仍可能略高

[JDK-8297247](https://bugs.openjdk.org/browse/JDK-8297247) 为 G1 增加了对 Remark 和 Cleanup 停顿时间的 MXBean 统计。此前这些阶段没有计入 G1 的 `GarbageCollectorMXBean`，但 `jstat` 的 `CGCT` 已经包含相关时间，两个观测渠道并不一致。

从 JDK 20 开始，Remark 和 Cleanup 被纳入 MXBean 后，使用 `getCollectionTime()` 汇总 GC 时间的监控系统会看到自然上涨。这个变化代表统计更完整，并不一定意味着应用实际多经历了同等规模的新增停顿。

因此，跨 JDK 版本比较 GC 指标时，应先确认：

- 采集源是 GC 日志、JFR、`jstat`，还是 MXBean；
- 不同版本是否统计相同的 GC 阶段；
- 指标上涨是否伴随吞吐下降或延迟恶化。

## 七、排查方法总结

这次问题可以归纳为一条通用排查链路：

1. **拆分现象**：区分真实停顿、GC 频率和统计值变化。
2. **固定变量**：保持工作负载、数据规模和 JVM 参数一致。
3. **版本二分**：先定位行为开始变化的 JDK 版本。
4. **按 GC Cause 聚类**：不要只看总时间，优先识别新增的触发原因。
5. **回溯 HotSpot 变更**：结合提交记录理解机制变化，而不是盲目调参。
6. **构造单变量实验**：例如扩大 Code Cache，以验证触发频率是否与容量相关。
7. **同时校验统计口径**：避免把可观测性变化误判为性能回退。

## 结论

JDK 21 升级后的 GC 时间上涨并非单一问题：

- 一部分来自 Code Cache 回收触发逻辑过于激进，造成额外的 GC 周期；
- 另一部分来自 G1 MXBean 统计范围扩大，是指标口径变化，而非等比例的实际性能退化。

这类问题提醒我们：**跨 JDK 版本做性能对比时，既要比较运行时行为，也要比较观测语义。** 如果只看一个聚合后的“GC 时间”，很可能把真实回归与统计变化混在一起，最终在错误的方向上调参。
