---
title: 从频繁 Full GC 到任务崩溃：一次 Metaspace 碎片化问题排查
date: 2022-06-02
categories:
  - jvm
tags:
  - java
  - metaspace
  - full-gc
  - fragmentation
  - troubleshooting
  - classloader
  - memory
excerpt: Full GC 反复触发、堆内存却不紧张？根因可能在 Metaspace 的碎片化——从 Metadata GC Threshold 到 Last ditch collection 的排查与修复。
---

# 从频繁 Full GC 到任务崩溃：一次 Metaspace 碎片化问题排查

在类动态生成、频繁部署或 ClassLoader 生命周期复杂的 Java 应用中，堆内存可能并不紧张，进程却仍然反复触发 Full GC，甚至最终因元数据分配失败而崩溃。

这类问题的关键往往不在 Java Heap，而在 **Metaspace**。

本文结合一次实际排查过程，介绍如何从 GC 日志识别元数据分配问题，理解旧版 Metaspace 的内存组织方式，并判断问题究竟来自类加载器泄漏、容量上限，还是内存碎片。

## 1. 问题现象

应用运行一段时间后开始密集出现以下 GC Cause：

```text
GC (Metadata GC Threshold)
Full GC (Metadata GC Threshold)
GC (Last ditch collection)
Full GC (Last ditch collection)
```

典型日志如下：

```text
[GC (Metadata GC Threshold)
 [PSYoungGen: 1600083K->32294K(3070976K)]
 4448340K->2883410K(9799680K), 0.0391263 secs]

[Full GC (Metadata GC Threshold)
 [PSYoungGen: 32294K->0K(3070976K)]
 [ParOldGen: 2851115K->947011K(6728704K)]
 2883410K->947011K(9799680K),
 [Metaspace: 137114K->78749K(1275904K)], 1.3952960 secs]

[GC (Last ditch collection) ...]
[Full GC (Last ditch collection) ...]
```

这里有两个重要信号：

1. Full GC 由 `Metadata GC Threshold` 触发，而不是老年代空间不足。
2. 随后出现 `Last ditch collection`，说明 JVM 在一次元数据分配失败后，常规 GC 和扩容尝试仍未满足分配请求，只能执行最后一次更激进的回收。

因此，排查重点应从 Java Heap 转向 Metaspace 分配路径。

## 2. 正确理解 Metaspace 指标

一次故障现场中的堆摘要可能类似：

```text
Metaspace       used 63445K, capacity 68515K, committed 249984K, reserved 1263616K
 class space    used 7859K, capacity 8410K, committed 35112K, reserved 1048576K
```

这些数值不能简单地理解为“Metaspace 已经用了 1.2 GB”。它们分别表示：

- `used`：已被类元数据实际使用的空间。
- `capacity`：已分配给各个 ClassLoader 元数据空间的 chunk 容量总和。
- `committed`：已经提交、可由进程实际访问的虚拟内存。
- `reserved`：JVM 预留的虚拟地址空间，并不等于实际物理内存占用。

`class space` 是压缩类指针启用后用于存放类相关元数据的独立空间，指标含义与上述类似。

因此，判断 Metaspace 压力时，不能只看 `reserved`；应同时观察：

- 已加载类与 ClassLoader 的数量是否持续增长；
- `used`、`committed` 和 GC threshold 的变化；
- 空闲 chunk 的数量和分布；
- Full GC 后是否有 ClassLoader 被卸载；
- 是否设置了过小的 `MaxMetaspaceSize`；
- 本次分配请求是否因连续空间不足而失败。

## 3. 旧版 Metaspace 为什么容易产生碎片

在 JDK 8 的实现中，Metaspace 从操作系统预留虚拟地址空间，并按需提交内存。其分配结构可以简化为：

```text
Virtual space
  └── Metachunk（分配给某个 ClassLoader）
        └── metadata block（类元数据的实际分配单元）
```

不同 ClassLoader 会获得不同规格的 chunk。以 64 位系统中的典型配置为例：

| Chunk 类型 | Class space | Non-class space |
| --- | ---: | ---: |
| specialized | 1 KB | 1 KB |
| small | 2 KB | 4 KB |
| medium | 32 KB | 64 KB |

当 ClassLoader 被卸载后，它占用的 chunk 会进入空闲列表，理论上可供后续分配复用。但旧实现存在两个限制：

1. 空闲 chunk 的规格可能与新请求不匹配；
2. 部分空闲内存分散在不同位置，虽然总量可观，却无法满足特定的连续分配请求。

结果是：**空闲内存很多，不代表本次分配一定成功。** JVM 可能继续提交新内存；当扩展受到限制或无法满足请求时，就会触发元数据 GC。

此外，旧实现通常只有在较大粒度的虚拟空间整体空闲后，才容易将内存归还给操作系统。ClassLoader 的创建与卸载模式不理想时，内部碎片和较高的 committed footprint 会长期存在。

## 4. 元数据分配失败后 JVM 做了什么

JDK 8 中，元数据分配失败后的处理流程大致如下：

1. 再次尝试直接分配，避免重复触发 GC；
2. 对支持并发收集的收集器，尝试扩展 Metaspace 并发起并发 GC；
3. 以 `Metadata GC Threshold` 为原因执行一次 GC，此时不主动清除软引用；
4. GC 后先在现有空间中重试分配；
5. 允许扩展 Metaspace 后再次尝试；
6. 仍然失败时，以 `Last ditch collection` 为原因再次 GC，并清理软引用；
7. 最终分配仍失败，则进入元数据 OOM 处理路径。

对应的核心逻辑可在 JDK 8 HotSpot 的 `VM_CollectForMetadataAllocation::doit()` 中找到。

`Last ditch collection` 并不直接证明存在碎片，但它能证明：**一次元数据分配已经经历常规回收、扩展和重试，仍未成功。** 后续必须结合 ClassLoader、chunk 空闲列表和容量限制继续判断。

## 5. 如何验证是否为碎片问题

### 5.1 先排除更常见的原因

在得出“碎片化”结论前，应依次排查：

1. **ClassLoader 泄漏**：ClassLoader 数量和已加载类数量是否持续单调增长；卸载后是否仍被线程、ThreadLocal、缓存或 JNI 引用。
2. **容量上限**：是否显式设置了 `-XX:MaxMetaspaceSize`，容器或进程地址空间是否限制扩展。
3. **类生成失控**：动态代理、反射生成器、脚本引擎、表达式编译器或字节码增强框架是否持续生成新类。
4. **GC 配置**：是否允许类卸载；相关 GC 周期是否真正执行了 Class Unloading。
5. **分配碎片**：ClassLoader 能正常卸载，但空闲 chunk 很多，Metaspace 分配仍反复失败。

只有第 1～4 项无法解释现象，并且工具输出显示大量不可有效复用的空闲 chunk 时，碎片化判断才具有较强证据。

### 5.2 使用 `VM.metaspace` 观察内部结构

较新的 JDK 提供了更详细的诊断命令：

```bash
jcmd <pid> VM.metaspace
```

重点关注以下区域：

```text
Total Usage
Virtual space
Chunk freelists
Waste
MaxMetaspaceSize
Current GC threshold
```

例如：

```text
Chunk freelists:
  Non-Class:
    specialized chunks: ...
    small chunks:       ...
    medium chunks:      ...

Waste:
  Committed unused:     ...
  Free in chunks in use:...
  In free chunks:       ...
```

如果观察到以下组合，通常意味着碎片或复用效率问题值得重点怀疑：

- ClassLoader 能被卸载，类数量没有持续失控增长；
- `In free chunks` 很高；
- 某些规格的 chunk 大量空闲；
- Metaspace 的已用量不高，但元数据分配仍频繁触发 GC；
- Full GC 后短暂恢复，随后很快再次出现同类问题。

不过，单次快照仍不足以证明因果关系。最好按固定间隔连续采集多份 `VM.metaspace`、类加载统计和 GC 日志，观察趋势。

## 6. 修复方案

### 6.1 优先升级到 JDK 17 或更高的 LTS 版本

JDK 16 引入了 Elastic Metaspace（JEP 387），重新设计了 Metaspace 的内存管理方式，主要目标包括：

- 更及时地将未使用的 Metaspace 内存归还给操作系统；
- 降低元数据分配器的内存占用；
- 减少维护成本，并提升后续改进的灵活性。

对于确认受到旧版 Metaspace 碎片或 committed footprint 影响的应用，升级到 JDK 17 或更高 LTS 版本通常是最彻底的工程方案。

需要注意：升级并不能修复真正的 ClassLoader 泄漏。如果类加载器始终可达，新实现同样无法卸载它们对应的类元数据。

### 6.2 无法立即升级时的缓解措施

若短期内必须继续使用旧 JDK，可以考虑：

- 排查并修复 ClassLoader 泄漏或动态类生成失控；
- 减少短生命周期 ClassLoader 的创建频率；
- 检查 `MaxMetaspaceSize` 是否设置过小；
- 为 Metaspace 留出合理余量，降低分配失败触发 Full GC 的频率；
- 持续监控已加载类、ClassLoader、Metaspace used/committed 和 Full GC 次数；
- 在变更 GC 或类卸载参数前，通过压测验证副作用。

单纯增大 Metaspace 上限通常只能延缓问题。如果根因是泄漏，最终仍会耗尽；如果根因是碎片，它也只是增加可周转空间。

## 7. 结论

当 GC 日志连续出现 `Metadata GC Threshold` 和 `Last ditch collection` 时，应避免把问题简单归因于“堆内存不足”。更可靠的排查路径是：

1. 确认失败发生在 Metaspace 分配路径；
2. 区分 `used`、`committed` 与 `reserved`，避免误读虚拟地址空间；
3. 排查 ClassLoader 泄漏、动态类生成和容量上限；
4. 使用 `jcmd <pid> VM.metaspace` 检查 chunk 空闲列表和浪费分布；
5. 通过连续快照建立证据链，而不是依赖单次数据；
6. 对旧版分配器导致的碎片问题，优先升级到 JDK 17 或更高 LTS 版本。

这类故障的难点在于：从总量上看，Metaspace 可能仍有大量空闲空间；但从分配器视角看，合适大小、可立即复用的空间已经不足。理解这一点，是解释“明明有空闲内存，为什么还在 Full GC”的关键。

## 参考资料

- [JEP 387: Elastic Metaspace](https://openjdk.org/jeps/387)
- [Oracle Java 8 GC Tuning Guide: Other Considerations](https://docs.oracle.com/javase/8/docs/technotes/guides/vm/gctuning/considerations.html)
- [Metaspace Architecture](https://stuefe.de/posts/metaspace/metaspace-architecture/)
- [Analyzing Metaspace with `jcmd`](https://stuefe.de/posts/metaspace/analyze-metaspace-with-jcmd/)
