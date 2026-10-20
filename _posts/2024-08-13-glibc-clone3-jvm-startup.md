---
title: 一次 Java 虚拟机启动失败问题排查：Cannot create GC thread 背后的 glibc / clone3 兼容性
date: 2024-08-13
categories:
  - jvm
tags:
  - jvm
  - glibc
  - docker
  - seccomp
  - troubleshooting
excerpt: 新基础镜像中的 glibc 默认使用 clone3()，而旧版 Docker seccomp 策略无法正确处理，导致 JVM 误报 Out of system resources 启动失败。
---

# 一次 Java 虚拟机启动失败问题的排查：`Cannot create GC thread` 背后的 `glibc` / `clone3` 兼容性

## 背景

某流式计算任务在一类基于旧版 Docker 运行时的容器环境中启动失败，报错如下：

```text
There is insufficient memory for the Java Runtime Environment to continue.
Cannot create GC thread. Out of system resources.
```

表面上看，这像是“系统资源不足”导致 JVM 无法启动；但进一步排查后发现，真实原因并不是物理机内存不足，也不是 JDK 版本本身的问题，而是：

- 新基础镜像中的 `glibc` 版本较新；
- 新版 `glibc` 默认优先尝试 `clone3()` 系统调用来创建线程；
- 旧版 Docker / `seccomp` 策略没有正确支持 `clone3`；
- 导致线程创建失败，最终 JVM 无法创建 GC 线程并启动失败。

这类问题很容易被误判为“内存不够”或“JDK 有问题”，因此很值得单独记录。

---

## 现象

任务启动阶段直接失败，JVM 输出：

```text
There is insufficient memory for the Java Runtime Environment to continue.
Cannot create GC thread. Out of system resources.
```

从字面看，这会让人优先怀疑以下几个方向：

1. 宿主机内存、线程数或其他系统资源不足；
2. 某个特定 JDK 版本存在兼容性问题；
3. 容器镜像或运行时环境发生了变化。

---

## 初步排查：几个容易走偏的方向

### 1. 误以为是物理机资源不足

JVM 明确报出 `Out of system resources`，第一反应通常是宿主机资源不足。但当同样的问题在多台机器上稳定复现时，这个解释就站不住了：

- 如果是单机资源偶发不足，通常不会在多台机器上表现一致；
- 问题具备环境稳定复现特征，更像是镜像或运行时兼容性问题。

因此，“机器资源真的不够”这个方向可以较早排除。

### 2. 怀疑是 JDK 版本问题

由于现场使用的 JDK 版本与历史常用版本不同，也一度怀疑是 JDK 版本升级带来的兼容性问题。

但在替换为另一套 JDK 基础镜像后，问题依然存在，说明：

- 这不是某个特定 JDK 版本独有的问题；
- 更可能是 JDK 所运行的容器基础环境存在系统级兼容性问题。

### 3. 镜像方向逐渐浮出水面

当“物理资源不足”和“JDK 版本问题”两个方向都被排除后，排查重点自然转向基础镜像。

进一步确认后发现，失败任务使用的是基于较新 Linux 发行版构建的基础镜像；而问题正是从这里开始的。

---

## 关键转折：社区已有类似案例

检索公开资料后，可以找到与该现象高度一致的社区讨论，例如：

- Adoptium / Temurin 容器相关 issue
- Moby（Docker Engine）关于 `clone3` 与 `seccomp` 的修复提交

这些讨论给出的核心结论非常一致：

- 较新的基础镜像会带来较新的 `glibc`；
- 较新的 `glibc` 会默认尝试使用 `clone3()`；
- 老版本 Docker 默认 `seccomp` 策略对 `clone3` 处理不正确；
- 从而导致线程创建失败；
- Java 进程会在 very early startup 阶段失败，并表现为“无法创建 GC 线程”。

这时问题就从“JVM 看起来像内存不足”转成了“系统调用兼容性问题”。

---

## 根因分析

### `glibc` 为什么会影响 JVM 创建线程？

JVM 启动时需要创建多个线程，例如：

- GC 线程
- VM 线程
- 编译线程
- 其他内部工作线程

在线程创建过程中，底层最终会走到 libc 与内核系统调用层。

较新的 `glibc` 在某些发行版中会优先尝试 `clone3()`。它的行为大致是：

- 如果 `clone3()` 返回 `ENOSYS`（系统不支持），则回退到传统的 `clone()`；
- 如果返回的是其他错误（例如 `EPERM`），则认为这是致命失败，不再回退。

问题恰恰出在旧版 Docker 默认 `seccomp` 策略这里：

- 它没有正确为 `clone3` 定义规则；
- 某些情况下返回的不是可回退的 `ENOSYS`，而是 `EPERM`；
- 于是 `glibc` 不会再回退到 `clone()`；
- 线程创建直接失败；
- JVM 无法继续启动，于是报出 `Cannot create GC thread`。

### 为什么报错看起来像“内存不足”？

因为 JVM 在启动阶段并不能感知“真正的业务语义原因”，它只知道：

- 关键线程创建失败了；
- 当前运行时环境无法提供继续执行所需的系统资源。

于是最终表现为一种比较泛化的错误描述：

```text
Out of system resources
```

但这里的“system resources”并不一定是狭义的内存，也可能是线程创建相关的系统调用能力或安全策略兼容性。

---

## 具体验证

为了验证判断，可以直接切换基础镜像版本进行对比。

实验现象如下：

- 使用基于 Debian 11 的基础镜像时，任务能够正常启动；
- 使用基于 Debian 12 的基础镜像时，任务启动失败。

进一步对比 `glibc` 版本：

- Debian 11: `glibc 2.31`
- Debian 12: `glibc 2.36`

这与社区问题中的分界点是吻合的：

- 较新的 `glibc` 会优先使用 `clone3`；
- 在旧版 Docker 环境下会触发兼容性问题；
- 较老版本 `glibc` 不会走到这条失败路径，因此表现正常。

这基本可以确认，问题不是 Java 本身的逻辑错误，而是：

> **新基础镜像 + 新版 `glibc` + 旧版 Docker / `seccomp` 策略 = JVM 启动失败**

---

## 为什么另一些容器环境没有问题？

同一个任务在另一类基于 Kubernetes 的容器环境中可以正常运行。

这说明问题并不在应用本身，而在于底层容器运行时实现差异：

- 某些环境并不依赖这套旧版 Docker 运行时路径；
- 或其底层运行时 / 安全策略已经正确处理了 `clone3`；
- 因此不会触发线程创建失败。

换句话说，这是一个**特定运行时环境组合下的兼容性问题**，而不是“只要升级基础镜像 JVM 就一定挂”。

---

## 解决方案

### 根本方案

升级 Docker Engine / 容器运行时，使其默认 `seccomp` 策略能够正确处理 `clone3`。

这是最彻底的方案，因为随着发行版持续升级，未来越来越多的新基础镜像都会依赖新版 `glibc`，问题不会只停留在某一个镜像版本。

### 临时规避方案

如果短期内无法升级容器运行时，可以选择：

1. **回退基础镜像到较老发行版**，例如 Debian 11；
2. **自定义允许 `clone3` 的 `seccomp` 策略**；
3. 在受控范围内，避免直接切到依赖新版 `glibc` 的基础镜像。

在实际生产环境中，最容易落地的往往是第一种：

- 先把基础镜像回退到 Debian 11；
- 待底层运行时升级完成后，再推进到更新的发行版。

---

## 影响范围

这类问题通常会命中如下组合：

- Java 服务 / Java 计算任务
- 使用较新的基础镜像（例如 Debian 12 / Ubuntu 22.04 一类）
- 运行在较老版本 Docker 引擎或旧 `seccomp` 策略环境中

而在以下环境中，可能不受影响：

- 已升级容器运行时的环境
- 不依赖旧版 Docker `seccomp` 默认行为的环境
- 仍使用较老发行版基础镜像的环境

因此，真正需要关注的不是“JDK 某个小版本”，而是：

> **基础镜像版本、`glibc` 版本、容器运行时版本、`seccomp` 策略版本是否匹配。**

---

## 排查经验总结

这个案例里最容易踩的坑有两个：

### 1. 被 JVM 报错字面意思带偏

`Cannot create GC thread` + `Out of system resources` 很容易让人立刻去看：

- 内存是不是不够；
- ulimit 是否太小；
- 线程数是否达到上限。

这些方向并非完全错误，但如果问题具有“跨机器稳定复现、切镜像后行为变化明显”的特征，就应该尽快把关注点转向系统兼容性。

### 2. 低估基础镜像升级带来的系统级变化

很多时候大家会把镜像升级理解为“换了个 OS 版本”，但实际上这可能意味着：

- `glibc` 版本变化；
- 默认系统调用路径变化；
- 安全策略兼容性变化；
- 线程、进程创建行为变化。

对于 Java 这种高度依赖底层线程能力的运行时来说，这类变化完全可能表现为 JVM 启动失败。

---

## 一句话结论

这次问题的根因不是内存不足，也不是某个 JDK 版本 bug，而是：

> **新版基础镜像中的 `glibc` 默认使用 `clone3()`，而旧版 Docker / `seccomp` 环境无法正确兼容，导致 JVM 无法创建线程并启动失败。**

如果你的 Java 应用在升级基础镜像后突然出现：

```text
Cannot create GC thread
Out of system resources
```

请不要只盯着内存，优先检查：

- 基础镜像是否升级到了更新发行版；
- `glibc` 是否变新；
- Docker Engine / 容器运行时是否较老；
- `seccomp` 是否允许或正确处理 `clone3`。

---

## 参考资料

- Adoptium / Temurin 容器问题讨论：Java 在线程创建阶段失败与基础镜像升级相关
- Moby（Docker Engine）关于 `clone3` 的 `seccomp` 修复提交
- `glibc` 对 `clone3()` 与 `clone()` 回退逻辑的相关说明
