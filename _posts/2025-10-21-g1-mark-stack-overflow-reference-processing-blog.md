---
title: G1 GC 弱引用处理阶段 Mark Stack 溢出问题分析
date: 2025-10-21
categories:
  - jvm
tags:
  - g1-gc
  - mark-stack
  - reference-processing
  - troubleshooting
excerpt: G1 Remark 阶段因弱引用处理导致 Mark Stack 溢出，JVM Fatal Error 的根因分析与解决方案。
---

# G1 GC 弱引用处理阶段 Mark Stack 溢出问题分析

## 背景

某 Java 作业在运行过程中发生 JVM Fatal Error，崩溃点位于 G1 GC 的 Remark 阶段。错误日志的核心信息如下：

```text
# A fatal error has been detected by the Java Runtime Environment:
#
#  Internal Error (g1ConcurrentMark.cpp:1555)
#  fatal error: Overflow during reference processing, can not continue.
#  Please increase MarkStackSizeMax and restart.
#
# JRE version: OpenJDK Runtime Environment (17.0.9+11)
# Java VM: OpenJDK 64-Bit Server VM (17.0.9+11, mixed mode, tiered,
#          compressed oops, compressed class ptrs, g1 gc, linux-amd64)
# Problematic frame:
# V  [libjvm.so]  G1ConcurrentMark::weak_refs_work(bool)
```

从调用栈可以看到，当前线程是 `VMThread`，问题发生在：

```text
G1ConcurrentMark::weak_refs_work(bool)
G1ConcurrentMark::remark()
VM_G1PauseConcurrent::doit()
VM_Operation::evaluate()
VMThread::evaluate_operation(VM_Operation*)
VMThread::run()
```

这说明 JVM 在 G1 并发标记周期的 Remark 阶段处理弱引用时，检测到 Mark Stack 溢出，并主动触发了进程终止。

## 问题现象

崩溃日志中给出的提示是：

```text
Overflow during reference processing, can not continue.
Please increase MarkStackSizeMax and restart.
```

直觉上，这似乎意味着只要增大 `-XX:MarkStackSizeMax` 就可以规避问题。但实际排查发现，在部分 JDK 版本中，这个提示并不完全准确：单纯调大 `MarkStackSizeMax` 并不能解决该问题。

原因在于，相关版本的 G1 实现虽然提供了全局 Mark Stack 的扩容接口，但在引用处理阶段发生 Mark Stack 不足时，并没有真正触发动态扩容逻辑。因此，即便把 `MarkStackSizeMax` 设置得很大，也可能无法改变实际使用中的 Mark Stack 容量。

## G1 Mark Stack 的作用

G1 GC 的并发标记阶段需要从 GC Roots 出发遍历对象图，并标记所有可达对象。Mark Stack 是这个过程中的关键数据结构，用于保存仍需继续扫描的对象引用。

可以把它理解为并发标记过程中的“待处理对象栈”：

1. 标记线程发现一个尚未扫描的对象；
2. 将该对象或其后续引用压入 Mark Stack；
3. 后续从 Mark Stack 中取出对象继续扫描；
4. 直到对象图遍历完成。

如果对象图非常复杂、引用关系非常密集，或者引用处理阶段短时间内产生大量待扫描对象，Mark Stack 就可能出现容量不足。

在 G1 中，Mark Stack 相关参数主要有两个：

```cpp
product(size_t, MarkStackSizeMax, NOT_LP64(4*M) LP64_ONLY(512*M),
        "Maximum size of marking stack")
        range(1, (max_jint - 1))

product(size_t, MarkStackSize, NOT_LP64(32*K) LP64_ONLY(4*M),
        "Size of marking stack")
        constraint(MarkStackSizeConstraintFunc,AfterErgo)
```

其中：

- `MarkStackSize`：初始 Mark Stack 大小；
- `MarkStackSizeMax`：Mark Stack 允许扩展到的最大大小；
- 在 64 位平台上，`MarkStackSize` 默认通常是 `4MB`；
- `MarkStackSize` 必须小于或等于 `MarkStackSizeMax`；
- `MarkStackSizeMax` 的上限受参数范围约束，不能无限增大。

## 为什么 JVM 选择直接崩溃

这个 Fatal Error 与 OpenJDK 中的一个历史问题有关：`JDK-8202049`。

在引用处理阶段，如果 Mark Stack 已经溢出，G1 的 `is_alive` 判断可能不再可信。也就是说，GC 可能无法准确判断某个对象是否仍然存活。

这是一个非常危险的状态：

- 如果把仍然存活的对象误判为不可达，可能导致对象被错误回收；
- 错误回收可能进一步引发数据损坏、悬挂引用、随机崩溃等更难定位的问题；
- 与其让 JVM 在不可信的堆状态上继续运行，不如尽早失败。

因此，相关修复采用了 fail-fast 策略。当 G1 在引用处理期间发现 Mark Stack 溢出且无法安全恢复时，直接终止 JVM，并给出明确错误信息。

对应逻辑可以简化理解为：

```cpp
if (has_overflown()) {
  // 如果引用处理期间 Mark Stack 溢出，堆对象存活性判断可能不可信。
  // 为避免基于错误标记结果继续运行，直接终止 JVM。
  fatal("Overflow during reference processing, can not continue. "
        "Please increase MarkStackSizeMax and restart.");
  return;
}
```

更早的处理方式相对保守：检测到溢出后直接返回。但在引用处理场景下，这种做法可能掩盖风险，因为后续逻辑仍可能基于不完整或不可信的标记结果继续执行。

## 为什么调大 MarkStackSizeMax 不一定有效

问题日志建议增大 `MarkStackSizeMax`，但实际验证中，即使把该参数显著调大，问题仍可能复现。

关键原因是：

> `MarkStackSizeMax` 只是 Mark Stack 可以扩展到的上限；如果当前 JDK 实现没有在该路径上触发扩容，那么调大上限并不会增加实际可用容量。

换句话说，这里的问题不是“最大值不够大”，而是“溢出时没有及时扩容”。

这类问题容易造成排查误区：

1. 日志提示 `increase MarkStackSizeMax`；
2. 运维或业务侧调大该参数；
3. 问题仍然复现；
4. 继续增大参数，但收益有限甚至没有收益。

因此，在分析 JVM 参数时，需要区分：

- 参数是否只是一个上限；
- 实现路径是否真的会使用这个上限；
- 溢出发生时是否存在动态扩容逻辑；
- 扩容失败后是否有可靠的降级或重试机制。

## 更合理的修复方向：引用处理期间动态扩容

后续 OpenJDK 中已有相关改进思路：当 G1 在引用处理阶段发现 Mark Stack 不足时，不应立即退出，而应先尝试扩展全局 Mark Stack，直到达到 `MarkStackSizeMax`。

这个方案的核心点是：

1. 在引用处理期间检测到 Mark Stack 不足；
2. 优先尝试扩展全局 Mark Stack；
3. 如果扩展成功，继续完成引用处理；
4. 如果已经达到上限仍然无法满足需求，再触发失败处理。

这样可以避免因为初始 Mark Stack 太小而过早终止 JVM，也避免重新扫描堆带来的复杂性和额外风险。

## ChunkAllocator 的设计思路

相关实现依赖一种可增长的分块数组结构，可以在不复制已有元素的情况下扩展容量。

它的基本思想是：

- 整体结构类似“数组的数组”；
- 每个内部数组可以理解为一个 bucket 或 chunk；
- 第一个 bucket 的大小设置为 2 的幂；
- 后续新增 bucket 时，容量按倍数增长；
- 通过位运算或快速索引计算，可以把全局下标映射到对应 bucket 以及 bucket 内偏移。

这种结构的好处是：

1. **扩容成本低**：新增 bucket 即可，不需要整体复制旧数据；
2. **索引效率高**：利用 2 的幂大小简化地址计算；
3. **适合 Mark Stack 场景**：Mark Stack 在高峰期可能需要快速扩展，而平时又不希望长期占用过多内存。

可以简化理解为：

```text
bucket[0] -> chunk size N
bucket[1] -> chunk size 2N
bucket[2] -> chunk size 4N
bucket[3] -> chunk size 8N
...
```

每次扩容只需要增加新的 chunk，而不需要把已有内容搬迁到一段更大的连续内存中。

## 临时规避与长期修复

针对这类问题，可以分为临时规避和长期修复两类方案。

### 临时规避

可以尝试增大初始 Mark Stack：

```bash
-XX:MarkStackSize=128M
```

注意，这里更关键的是 `MarkStackSize`，而不只是 `MarkStackSizeMax`。

如果问题发生在没有动态扩容能力的 JDK 实现中，增大初始 Mark Stack 有机会降低溢出概率。但这仍然是规避手段，并不是根治方案。

### 长期修复

长期方案应升级到已经修复该问题的 JDK 版本，或者将引用处理期间 Mark Stack 动态扩容的补丁移植到当前维护的 JDK 分支中。

修复后的预期行为是：

- 正常情况下保持较小初始 Mark Stack，避免不必要内存占用；
- 遇到引用处理期间容量不足时，按需扩容；
- 只有在达到最大容量仍无法满足需求时，才触发失败处理。

这种方式比简单增大固定参数更稳健，也更符合 G1 在复杂对象图场景下的实际运行需求。

## 排查建议

如果线上遇到类似问题，可以按以下顺序排查：

1. **确认崩溃阶段**：检查 hs_err 日志中是否出现 `G1ConcurrentMark::weak_refs_work`、`remark`、`reference processing` 等关键字；
2. **确认 GC 类型**：确认 JVM 使用的是 G1 GC；
3. **确认错误信息**：检查是否存在 `Overflow during reference processing`；
4. **检查 JDK 版本**：确认当前版本是否包含引用处理期间 Mark Stack 动态扩容修复；
5. **区分参数含义**：不要只关注 `MarkStackSizeMax`，还要关注 `MarkStackSize` 以及具体实现是否会动态扩容；
6. **评估临时参数**：在无法立即升级 JDK 时，可以临时增大 `MarkStackSize`；
7. **优先推动版本修复**：如果问题可复现或影响稳定性，应优先升级到包含修复的 JDK 版本。

## 小结

这个问题的表面现象是 G1 GC 在 Remark 阶段处理弱引用时 Mark Stack 溢出，JVM 根据 fail-fast 策略主动崩溃。日志提示增大 `MarkStackSizeMax`，但在部分 JDK 实现中，单纯调大该参数并不能解决问题，因为对应路径没有真正执行动态扩容。

更合理的修复方式是在引用处理期间检测 Mark Stack 不足时，先尝试扩展全局 Mark Stack，直到达到 `MarkStackSizeMax`；只有扩容仍无法满足需求时，才终止 JVM。

实践上，短期可以通过增大 `-XX:MarkStackSize` 降低触发概率，长期应升级到包含该修复的 OpenJDK 版本，或将相关补丁移植到当前维护分支中。
