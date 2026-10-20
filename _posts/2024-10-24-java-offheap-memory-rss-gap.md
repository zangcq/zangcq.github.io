---
title: Netty 堆外内存没涨，RSS 却一直涨？记一次 glibc Arena 排查
date: 2024-10-24
categories:
  - jvm
tags:
  - java
  - netty
  - glibc
  - memory
  - rss
  - troubleshooting
excerpt: Netty 统计的直接内存在阈值内，但进程 RSS 高出几个 G。排查发现差值来自 glibc malloc 的 Arena 缓存——应用释放了内存，但 glibc 没还给操作系统。
---

## 问题概述

有一个基于 Netty 的高并发 Java 服务，内存指标出现了奇怪的偏差：

- Java 堆在 `-Xmx` 限制内，用量正常；
- Netty 统计的直接内存没超过业务阈值；
- JVM Native Memory Tracking（NMT）显示大量内存归到 `Internal`；
- 但操作系统看到的 RSS 比 JVM 和 Netty 的统计值高出一大截。

调用链很快就指向了 Netty——分配路径很清楚，`Unsafe.allocateMemory` 进来的。但问题的关键不是"谁申请的"，而是：

> **Netty 觉得自己只用了 X GB，操作系统却看到 X+N GB。这 N GB 是哪来的？**

最终排查发现，差值主要来自 glibc `malloc` 的 Arena 缓存和归还策略。大量并发线程通过 Netty 申请小于 Arena 粒度的直接内存，即使上层释放了，glibc 也可能把空闲页继续留在进程 Arena 里，不通过 `munmap` / `brk` 还给操作系统。

## 1. 先分清楚是哪一层

Java 进程内存异常，第一步先建立分层视角：

- **Java Heap**：对象堆，`-Xms` / `-Xmx` 管着。
- **JVM Native Memory**：Metaspace、Code Cache、GC 结构、线程栈、JIT 等。
- **Direct Memory**：NIO、Netty 或业务通过 `Unsafe` 等方式分配的堆外内存。
- **JNI / Native Library**：本地库通过 `malloc`、`mmap` 分配的内存。
- **分配器缓存与碎片**：上层已经释放了，但分配器还没还回去。
- **文件映射和共享内存**：也反映在进程地址空间 / RSS 里。

这个 case 里堆稳定、没有 `Java heap space`，直接转向堆外排查。

## 2. pmap 先看个大概

```bash
pmap -X <pid> > pmap.txt
```

结果里出现了大量 64MB 的匿名映射块，排列整齐。64MB 这个数字很眼熟——glibc Thread Arena 的默认大小就长这样。

不过光看 `pmap` 只能说"这些地址段占了内存"，不能直接回答"谁申请的"。还得结合 NMT、调用栈和系统调用继续验证。

## 3. NMT 缩小范围

JVM 启动时加：

```bash
-XX:NativeMemoryTracking=detail
```

运行中查：

```bash
jcmd <pid> VM.native_memory summary
```

这个 case 的 NMT 里 `Internal` 分类显著偏大，初步判断大量内存来自 `Unsafe.allocateMemory`。但 NMT 有几个局限得注意：

- 它跟踪的是 JVM 自身或经 JVM 记账的 Native 内存，不等于操作系统 RSS；
- `reserved`、`committed` 和 RSS 是三个不同的东西；
- 分配器缓存、碎片和部分第三方 native 分配可能归因不准。

NMT 更适合"定界"，别拿它当最终结论。

## 4. Native 火焰图为什么没直接解决问题

常见思路是用 jemalloc 接管 `malloc/free` 生成火焰图：

```bash
LD_PRELOAD=/path/to/libjemalloc.so java ...
```

这对纯 C/C++ 调用栈很有效，但 native 栈跨越到 JIT 生成的 Java 代码后，经常只剩地址，还原不了完整 Java 栈帧。

也可以用 async-profiler 的 native 分配事件：

```bash
./profiler.sh -d <duration> -e malloc -f malloc.html <pid>
```

但这个 case 里受采样时机、符号信息和调用路径的影响，没拿到能定位问题的完整调用栈。

> 关于 jemalloc profiling 定位 native 内存泄漏的方法，可以参考[上一篇文章](/posts/java-native-memory-leak-jemalloc/)。

## 5. 从 Netty 统计与 RSS 的差值入手

业务侧用 Netty 分配器指标统计直接内存：

```java
PooledByteBufAllocator.DEFAULT.metric().usedDirectMemory();
```

监控显示 Netty 使用量在阈值内，但 `pmap` 汇总的匿名映射 RSS 明显更大。这说明至少存在两种统计口径：

- **Netty 视角**：自己管着、还在用的内存块；
- **操作系统视角**：进程当前驻留在物理内存里的页面。

上层释放了内存，分配器可能继续缓存这些页面。Netty 的使用量会降，RSS 不一定同步降。

## 6. 在 Unsafe.allocateMemory 抓 Java 调用栈

在可控测试环境里，用带调试能力的 JDK 在 `Unsafe.allocateMemory` 路径上加了采样日志。至少记录：线程名、申请字节数、时间戳、返回地址、Java 调用栈，加个采样率或最小分配阈值避免日志风暴。

拿到了核心调用链：

```text
jdk.internal.misc.Unsafe.allocateMemory
sun.misc.Unsafe.allocateMemory
io.netty.util.internal.PlatformDependent0.allocateDirectNoCleaner
io.netty.util.internal.PlatformDependent.allocateDirectNoCleaner
io.netty.buffer.PoolArena$DirectArena.allocateDirect
io.netty.buffer.PoolArena$DirectArena.newChunk
io.netty.buffer.PoolArena.allocateNormal
io.netty.buffer.PooledByteBufAllocator.newDirectBuffer
io.netty.buffer.AbstractByteBufAllocator.directBuffer
io.netty.channel.nio.AbstractNioByteChannel$NioByteUnsafe.read
io.netty.channel.nio.NioEventLoop.run
java.lang.Thread.run
```

确认了堆外分配走的是 Netty 的 `allocateDirectNoCleaner` 路径，底层 `Unsafe.allocateMemory`。但这只解释了"谁在申请"，还没解释"释放了为什么 RSS 不降"。

## 7. strace 看 mmap 和 munmap 是否匹配

继续跟内存相关的系统调用：

```bash
strace -f -k -p <pid> -e mmap,munmap,brk
```

看统计的话：

```bash
strace -f -p <pid> -e mmap,munmap,brk -c
```

结果 `mmap` 和 `munmap` 的调用次数明显不对等：进程一直在申请新映射，但没有以同样的节奏释放。结合 `pmap` 里重复出现的大块匿名映射，链路已经比较清晰了：

1. Netty 频繁申请直接内存；
2. `Unsafe.allocateMemory` 最终进 glibc `malloc`；
3. 高并发线程触发或使用多个 Arena；
4. Netty 释放了部分内存，glibc 留着在 Arena 里复用；
5. Netty 统计的"在用内存"降了，但操作系统 RSS 不降。

## 8. glibc Arena 为什么让 RSS 膨胀

glibc `malloc` 为了减少多线程分配锁竞争，维护了一个 Main Arena 和多个线程相关的 Arena。不同线程可以在不同 Arena 上操作，并行分配，吞吐量上去了。

代价呢：

- 每个 Arena 都可能保留空闲块；
- 空闲块只有满足特定条件时才会通过 `malloc_trim`、`munmap` 等方式归还；
- 跨 Arena 的空闲空间没法合并；
- 线程多、分配模式不规则时，缓存和碎片会让 RSS 远高于上层统计值。

所以"应用释放了内存"不等于"操作系统 RSS 马上降"：

```text
RSS ≈ 仍在使用的内存
    + 分配器缓存
    + 内外部碎片
    + 其他驻留映射
```

Netty 指标和 RSS 之间那 N GB 的差值，就是 glibc Arena 里还没还给操作系统的页面。

## 9. 方案一：HotSpot Native Heap Trimming

OpenJDK 在较新版本里提供了周期性 Native Heap Trimming，定时调 glibc `malloc_trim(3)`，把未使用的 native heap 页面还给操作系统。

相关 JBS issue：

- [JDK-8293114: JVM support for Linux native heap trimming](https://bugs.openjdk.org/browse/JDK-8293114)
- [JDK-8315028: Backport for JDK 17](https://bugs.openjdk.org/browse/JDK-8315028)
- [JDK-8314107: Backport for JDK 21](https://bugs.openjdk.org/browse/JDK-8314107)

### 周期性触发

```bash
java \
  -XX:+UnlockExperimentalVMOptions \
  -XX:TrimNativeHeapInterval=10000 \
  -jar app.jar
```

部分新版本可能已经不需要实验选项了。先确认自己 JDK 是否支持：

```bash
java -XX:+PrintFlagsFinal -version | grep TrimNativeHeapInterval
```

别无脑设很短的间隔。`malloc_trim` 要扫描和回收空闲页，太频繁会带来 CPU 开销、锁竞争和延迟抖动。建议在压测环境里对比：

- RSS 回落幅度；
- trim 单次耗时；
- CPU 使用率；
- P99/P999 延迟；
- 后续重新分配导致的 page fault。

### 观察 trim 日志

```bash
java -Xlog:trimnative=debug:nativeheap.log ...
```

### 手动触发

```bash
jcmd <pid> System.trim_native_heap
```

手动触发很适合验证"高 RSS 是不是 glibc 可回收缓存造成的"——如果命令执行后 RSS 明显下降，就是很硬的证据了。

相关 issue：[JDK-8268893: Add a JCmd to trim the glibc heap](https://bugs.openjdk.org/browse/JDK-8268893)

## 10. 方案二：换成 jemalloc

另一种思路是通过 `LD_PRELOAD` 切分配器：

```bash
LD_PRELOAD=/path/to/libjemalloc.so java -jar app.jar
```

jemalloc 和 glibc 的 Arena、size class、decay、页面回收策略都不一样。在某些高并发 Java/Netty 场景里，确实能降低 RSS 峰值、改善回收可预测性。

但切换分配器不是免费午餐，得用真实负载验证：

- 吞吐和尾延迟有没有变化；
- RSS 峰值和稳态值有没有下降；
- page fault 有没有增加；
- native 分配 CPU 开销怎么样；
- 和用的 JNI 库兼不兼容；
- decay、tcache、Arena 数量是不是适合当前负载。

也可以试更激进的回收配置：

```bash
MALLOC_CONF="narenas:1,tcache:false,dirty_decay_ms:0,muzzy_decay_ms:0"
```

但这类配置会显著改变分配吞吐、缓存命中和锁竞争，千万别不测试就上生产。

## 11. Netty 参数也别忘了查

调用栈里看到用了 `allocateDirectNoCleaner`，还得确认 Netty 自己的直接内存限制：

```bash
-Dio.netty.maxDirectMemory=<bytes>
```

`-XX:MaxDirectMemorySize` 和 `-Dio.netty.maxDirectMemory` 的关系取决于 Netty 版本、平台能力和具体分配路径，尤其在 no-cleaner 路径下，不能假设 JVM 参数就能约束 Netty 的全部直接内存。

建议验证：

1. 确认 Netty 版本和 `PlatformDependent` 的参数解析逻辑；
2. 启动时打印实际生效的 direct memory limit；
3. 构造可控分配测试，看超过阈值后的表现；
4. 对照 Netty metric、NMT、`pmap`、RSS；
5. 区分"上层在用"和"分配器已缓存"的内存。

顺便提一嘴：`MALLOC_ARENA_MAX` 可以限制 Arena 数量，但值太小会加剧分配锁竞争。当压测变量用还行，别当默认修复方案。

## 12. 一套可复用的排查流程

以后再碰到类似问题，按这个顺序走：

### 先建统一时间窗口

同时记录：容器 RSS、Heap used/committed、Netty direct memory、NMT summary、线程数、请求吞吐延迟、Full GC、page fault。数据不在同一时间窗口的话，差值分析很容易失真。

### 区分容量、使用量、驻留量

- `reserved`：预留的虚拟地址空间；
- `committed`：已提交的内存；
- allocator used：上层认为还在用的；
- RSS：实际驻留在物理内存里的。

别把不同口径的指标直接对比。

### 逐层归因

```text
业务/框架指标
  → JVM NMT
  → Java/Native 分配调用栈
  → pmap/smaps 地址区间
  → mmap/munmap/brk 系统调用
  → 手动 trim 或替换分配器验证
```

### 用可逆实验验证

优先低风险、结果明确的实验：

- 手动执行一次 `System.trim_native_heap`；
- 隔离环境降低并发线程数；
- 对比 glibc 和 jemalloc；
- 调整 Netty direct memory limit；
- 调整 `MALLOC_ARENA_MAX`；
- 相同流量模型下对比 RSS 和尾延迟。

别靠一个工具的一次截图就宣布根因。

## 13. 总结

这次排查最值得带走的三个点：

1. **框架内存指标不等于进程 RSS。** Netty 统计的是自己管理视角下的使用量，操作系统统计的是驻留页，中间还隔着 libc 分配器。
2. **定位分配来源和解释 RSS 放大是两个问题。** `Unsafe.allocateMemory` 调用栈证明内存来自 Netty，`pmap`、`strace` 和 trim 实验才解释释放后 RSS 为什么不降。
3. **修复得同时考虑内存和性能。** 周期性 `malloc_trim`、jemalloc、`MALLOC_ARENA_MAX`、Netty 限制都可能有效，但也都可能引入 CPU、锁竞争、page fault 或尾延迟的代价。

当 Java 服务出现"堆不大、NMT 好像能解释一部分、RSS 却一直涨"时，把 glibc Arena 和分配器缓存放进排查清单。真正靠得住的结论，由上层调用栈、地址空间分布、系统调用和可逆实验一起组成。

> 相关阅读：[使用 jemalloc 定位 Java Native Memory 泄漏](/posts/java-native-memory-leak-jemalloc/)——另一个 native 内存排查案例，根因在 `GZIPOutputStream` 未关闭。[一次 Flink Full GC 频繁问题排查：真正的根因竟是 CPU Throttling](/posts/flink-full-gc-cpu-throttling-rca/)——GC 不一定起于 JVM，有时在操作系统层。

## 参考资料

- [JDK-8293114: JVM support for Linux native heap trimming](https://bugs.openjdk.org/browse/JDK-8293114)
- [JDK-8315028: Backport for JDK 17](https://bugs.openjdk.org/browse/JDK-8315028)
- [JDK-8314107: Backport for JDK 21](https://bugs.openjdk.org/browse/JDK-8314107)
- [JDK-8268893: Add a JCmd to trim the glibc heap](https://bugs.openjdk.org/browse/JDK-8268893)
- [HotSpot developers mailing list: native heap trimming discussion](https://mail.openjdk.org/pipermail/hotspot-dev/2021-August/054323.html)
- [Oracle Java Troubleshooting Guide: Native Memory Tracking](https://docs.oracle.com/javase/8/docs/technotes/guides/troubleshoot/tooldescr007.html)
- [glibc malloc internals overview](https://www.openeuler.org/en/blog/wangshuo/Glibc%20Malloc%20Principle/Glibc_Malloc_Principle.html)