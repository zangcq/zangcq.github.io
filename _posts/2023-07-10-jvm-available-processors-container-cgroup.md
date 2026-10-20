---
title: 在容器里 Runtime.availableProcessors() 为什么会"变大"？从 HotSpot 的 active CPU 计算说起
date: 2023-07-10
categories:
  - jvm
tags:
  - jvm
  - container
  - cgroup
  - cpu
  - troubleshooting
excerpt: 容器分配 2 核，JVM 却读到 96 核——梳理 HotSpot 在不同 JDK 版本、cgroup v1/v2、quota/shares/affinity 下计算 active processor count 的完整逻辑。
---

# 在容器里 `Runtime.availableProcessors()` 为什么会"变大"？——从 HotSpot 的 active CPU 计算说起

## 背景

某业务在容器环境中启动时，会根据 `Runtime.getRuntime().availableProcessors()` 计算默认工作线程数。业务方观测到：容器明明只分配了很少的 CPU（例如 2 核），但 JVM 读到的可用 CPU 数却接近宿主机总核数（例如 96 核），从而导致线程数膨胀并触发资源/配额类的启动失败。

这类问题的关键在于：**`availableProcessors()` 的实现最终取决于 HotSpot 对“active processor count”的判定，而这在容器/cgroup、绑核、JDK 版本差异下会出现显著变化。**

---

## 最小复现

用一个最小 Java 程序直接打印 `availableProcessors()`：

```java
public class AvailableProcessor {
    public static void main(String[] args) {
        int processors = Runtime.getRuntime().availableProcessors();
        System.out.println("Available processors: " + processors);
    }
}

// javac AvailableProcessor.java
// java AvailableProcessor
```

---

## `availableProcessors()` 到底是什么

JDK 文档：`Runtime.availableProcessors()` 返回“Java 虚拟机可用的处理器数量”，并且该值在 JVM 生命周期中可能变化（需要敏感的应用应当周期性轮询并调整资源使用）。

HotSpot 调用链（概念层面）大致如下：

- `Runtime.availableProcessors()`（native）
- `JVM_ActiveProcessorCount()`
- `os::active_processor_count()`

因此问题可以收敛为：**`os::active_processor_count()` 在不同版本/不同容器限制下如何计算。**

---

## 早期实现：不识别容器（只看宿主机在线 CPU）

在较早的实现中，Linux 上的 active CPU 数主要来自：

- `sysconf(_SC_NPROCESSORS_ONLN)`：宿主机在线 CPU 数（容器不感知）

这会导致：**即使容器限制了 CPU，JVM 仍可能看到宿主机总核数**。

---

## 引入“进程可用 CPU”概念：`sched_getaffinity`（考虑绑核/cpuset）

后来 HotSpot 引入了通过 `sched_getaffinity` 读取进程 CPU 亲和性（或 cpuset）来计算 active CPU：

- `sched_getaffinity(0, ..., &cpus)` 得到当前进程允许运行的 CPU mask
- 失败则 fallback 到 `sysconf(_SC_NPROCESSORS_ONLN)`

这使得在一些“绑核/限制 cpuset”的场景下，JVM 至少不会无脑返回宿主机全部在线 CPU。

---

## 容器感知：cgroup v1 的 CPU 限制如何影响 JVM

当 HotSpot 识别到运行在容器中时，会额外读取 cgroup 信息来限制 CPU 数。整体思路是从三类来源择优：

1. **用户显式覆盖**：`-XX:ActiveProcessorCount=<N>`（最高优先级）
2. **OS 层面**：`sched_getaffinity` / `sysconf`
3. **cgroup CPU 子系统**：从 quota/period、shares 等信息推导 CPU 数

### cgroup v1：quota / period / shares 的计算

- quota/period：
  - 若设置了 quota（非 -1），则 `quota_count = ceil(quota / period)`
- shares：
  - 若设置了 shares（且不是默认值），则 `share_count = ceil(shares / 1024)`
- 若两者都存在，会根据一个开关决定取 quota 或取 `min(quota_count, share_count)`（实现上有相关 flag 控制）
- 最终结果还会结合 OS 层得到的 `cpu_count`（来自 affinity/cpuset）：
  - `result = min(cpu_count, limit_count)`

**要点：即使 quota 算出来是 20，如果进程 affinity 只允许 19 个 CPU，那么最终也可能返回 19。**

### 排查建议（对外通用版）

- 打开容器/OS 相关日志（不同 JDK 版本日志开关略有差异），观察 JVM 读取到的：
  - cgroup 路径
  - quota/period、shares
  - affinity/cpuset 计算的 cpu_count
- 同时在容器里检查：
  - `cat /proc/self/status | grep Cpus_allowed_list`
  - cgroup v1 下 `cpu.cfs_quota_us`、`cpu.cfs_period_us`、`cpu.shares`
  - cpuset 配置（如 `cpuset.cpus`）

---

## cgroup v2：`cpu.max` 与 `cpu.weight`

cgroup v2 中：
- quota / period 由 `cpu.max` 提供（格式类似：`<quota> <period>`，也可能是 `max <period>` 表示无限制）
- shares 的替代字段是 `cpu.weight`（但其与 v1 的 shares 并非线性等价，需要映射/缩放）

因此在 v2 上 JVM 的读取路径/计算方式会变更，常见现象是：
- quota 限制生效时 `availableProcessors()` 更接近预期（例如 4）
- shares 映射涉及更多换算逻辑，不同版本行为可能变化

---

## 版本变化与兼容性风险：CPU shares 的“破坏性变更”

在较新的更新中，社区曾引入一个重要变更：**默认不再使用 CPU shares 来计算 active processor count**（原因包括：可能导致 CPU 利用不足、默认值 1024 的语义在不同平台/编排系统下不一致等）。

相关公开信息（对外可引用）：
- OpenJDK commit：Do not use CPU Shares to compute active processor count（对应 JDK bug/讨论中解释了行为变化与理由）
- Workaround：一些版本提供临时开关（例如 `-XX:+UseContainerCpuShares`）用于恢复旧行为（具体可用性取决于版本）

**对外结论表达建议**：

> 如果你的业务曾依赖“CPU shares 影响 `availableProcessors()`”这一行为，那么在 JDK 小版本升级后可能出现线程数/并发度突变，需要在升级评估中专门验证，并考虑用显式 `-XX:ActiveProcessorCount` 或业务侧并发度上限来稳定行为。

---

## 总结

1. `Runtime.availableProcessors()` 在 HotSpot 中最终落到 `os::active_processor_count()`，其结果会受 **JDK 版本**、**容器/cgroup**、**quota/period/shares**、以及 **cpuset/绑核（affinity）** 共同影响。
2. 在容器里 CPU quota 生效并不意味着 JVM 一定返回 quota 推导出来的核数，因为最终还会取 `min(cpu_count(from affinity), limit_count(from cgroup))`。
3. cgroup v2 引入了 `cpu.max`/`cpu.weight`，并且 shares 的语义映射更复杂；同时社区也曾调整“是否使用 shares 参与计算”的策略，导致升级风险。
4. 面对不可控环境差异，最稳妥的工程手段通常是：
   - JVM 侧显式设定 `-XX:ActiveProcessorCount=<N>`（如果你希望固定可用核数）
   - 业务侧并发/线程池设置上限，避免“读到大核数→线程数爆炸”的链式故障
