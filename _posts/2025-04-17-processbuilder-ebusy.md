---
title: JDK 17 下 ProcessBuilder.start() 偶发 error=16, Device or resource busy 的排查与分析
date: 2025-04-17
categories:
  - jvm
tags:
  - jvm
  - jdk17
  - processbuilder
  - jemalloc
  - troubleshooting
excerpt: jemalloc 统计 socket 占用了 fd 3，与 JDK posix_spawn() 的 fail pipe 发生 dup2() 竞争，导致 ProcessBuilder.start() 偶发 EBUSY。
---

# JDK 17 下 ProcessBuilder.start() 偶发 `error=16, Device or resource busy` 的排查与分析

> 本文由一次线上排障记录整理而来，已去除业务名称、内部仓库、内部平台链接、机器信息、人员信息和具体项目标识，仅保留技术分析过程与可复用结论。

## TL;DR

在 JDK 17 环境中，Java 应用通过 `ProcessBuilder.start()` 启动子进程时，偶发抛出：

```text
java.io.IOException: Cannot run program "python": error=16, Device or resource busy
Caused by: java.io.IOException: error=16, Device or resource busy
    at java.base/java.lang.ProcessImpl.forkAndExec(Native Method)
```

最终定位到：**JDK 9+ 默认使用 `posix_spawn()` 创建子进程，在子进程初始化阶段会将失败报告管道移动到固定 fd 3；如果进程中预加载的 `jemalloc` 统计服务恰好占用了 fd 3，并且该 fd 处于内核认为“已分配但尚未完成初始化”的状态，`dup2(fail_pipe_fd, 3)` 可能返回 `EBUSY`，导致 Java 层表现为 `ProcessBuilder.start()` 失败。**

关键结论：

1. 该问题不是 Python 脚本本身导致的；将启动命令替换为 `ls` 也能复现。
2. 该问题与 JDK 9+ 的 `posix_spawn()` 路径有关，JDK 8/11/17 的表现可能因为 fd 分配顺序、GC 日志文件、预加载库初始化时机不同而不同。
3. `EBUSY` 来自 Linux kernel `dup2/dup3` 的特殊竞争场景：目标 fd 已标记 open，但还没有可释放的 `struct file`。
4. 临时止损方案是移除或禁用 `LD_PRELOAD=jemalloc.so` 中相关统计服务。
5. 更稳妥的长期方案是让 jemalloc 的统计/诊断 socket 可通过环境变量显式开关，避免默认占用低编号 fd，尤其是 fd 3。

## 问题现象

某 Java 流式任务升级到 JDK 17 后，少量 worker 实例在初始化阶段偶发失败。失败点集中在通过 Java 启动外部子进程时：

```java
Caused by: java.lang.RuntimeException: Subprocess Init failed.
    at example.SubProcess.init(SubProcess.java:88)
    at example.SubProcess.<init>(SubProcess.java:44)
    ...
Caused by: java.io.IOException: Cannot run program "python": error=16, Device or resource busy
    at java.base/java.lang.ProcessBuilder.start(ProcessBuilder.java:1143)
    at java.base/java.lang.ProcessBuilder.start(ProcessBuilder.java:1073)
    ...
Caused by: java.io.IOException: error=16, Device or resource busy
    at java.base/java.lang.ProcessImpl.forkAndExec(Native Method)
    at java.base/java.lang.ProcessImpl.<init>(ProcessImpl.java:314)
    at java.base/java.lang.ProcessImpl.start(ProcessImpl.java:244)
    at java.base/java.lang.ProcessBuilder.start(ProcessBuilder.java:1110)
```

初始观察有两个特征：

- 不是所有 worker 都失败，问题具有概率性。
- 同一任务在较低版本 JDK 上未稳定复现，升级到 JDK 17 后更容易暴露。

因此最初的怀疑方向包括：

1. JDK 17 的子进程创建路径存在兼容性差异。
2. 运行环境或机器存在局部异常。
3. 被启动的 Python 脚本或其依赖文件存在并发读写冲突。

## 第一阶段：锁定异常抛出位置

Java 栈只能看到异常从 native 方法 `ProcessImpl.forkAndExec` 抛出，需要继续查看 OpenJDK 在 Unix 平台下的实现。

对应源码位于：

```text
src/java.base/unix/native/libjava/ProcessImpl_md.c
```

核心逻辑可以简化为：

```c
resultPid = startChild(env, process, c, phelperpath);

if (resultPid < 0) {
    switch (c->mode) {
      case MODE_VFORK:
        throwIOException(env, errno, "vfork failed");
        break;
      case MODE_FORK:
        throwIOException(env, errno, "fork failed");
        break;
      case MODE_POSIX_SPAWN:
        throwIOException(env, errno, "posix_spawn failed");
        break;
    }
    goto Catch;
}

close(fail[1]);

switch (readFully(fail[0], &errnum, sizeof(errnum))) {
case 0:
    break; // exec succeeded
case sizeof(errnum):
    waitpid(resultPid, NULL, 0);
    throwIOException(env, errnum, "Exec failed");
    goto Catch;
default:
    throwIOException(env, errno, "Read failed");
    goto Catch;
}
```

通过增加调试日志，确认异常来自：

```c
throwIOException(env, errnum, "Exec failed");
```

其中 `errnum = 16`，对应：

```text
EBUSY: Device or resource busy
```

这说明：子进程已经启动到某个阶段，但在真正 `exec` 目标程序之前，通过 fail pipe 将错误码 `16` 回传给父进程。

## 第二阶段：排除业务脚本竞争

一开始怀疑外部 Python 脚本存在并发问题：多个 Python 进程可能同时下载、写入、读取同一目录，导致某些文件尚未准备完成就被另一个进程读取。

脚本逻辑可抽象为：

```python
import os
import random
import signal
import subprocess
import time

process = None

def signal_handler(signum, frame):
    if process and process.poll() is None:
        process.terminate()
    os._exit(1)

if __name__ == '__main__':
    product, version = sys.argv[-1].strip().split(':')
    tmp_dir = os.path.join('./deploy_tmp', version)

    checkout_cmd = ['artifact-cli', 'clone', '--version', version, product, tmp_dir]
    if not os.path.exists(tmp_dir):
        try:
            subprocess.check_call(checkout_cmd)
        except Exception:
            time.sleep(random.uniform(3, 10))

    argv_list = sys.argv[1:]
    argv_list.insert(0, './bin/build_instance')
    argv_list.append('-bin_path=' + tmp_dir)

    signal.signal(signal.SIGTERM, signal_handler)
    process = subprocess.Popen(argv_list, cwd=tmp_dir)
    process.wait()
```

确实可以发现一个潜在问题：如果目录已创建但内容尚未完整写入，另一个进程可能提前进入 `subprocess.Popen()`，从而触发类似 `Permission denied` 的错误。

但这条线索不能解释原问题：

```text
OSError: [Errno 13] Permission denied
```

这里的错误码是 `13`，不是 `16`。

进一步将 Java 侧启动命令从 `python` 替换成简单的 `ls`，仍然可以复现：

```text
Caused by: java.io.IOException: Cannot run program "ls": error=16, Device or resource busy
Caused by: java.io.IOException: error=16, Device or resource busy
    at java.base/java.lang.ProcessImpl.forkAndExec(Native Method)
```

因此，根因不在 Python 脚本本身，而在 JDK 创建子进程的路径上。

## 第三阶段：理解 JDK 9+ 的 `posix_spawn()` 路径

从 JDK 9 开始，Unix 平台上创建子进程的默认实现逐步转向 POSIX `posix_spawn()`，以替代传统的 `fork()/exec()` 路径。这样做的主要原因包括：

- 避免大进程 `fork()` 时产生过高内存开销。
- 降低多线程进程中 `fork()` 后只剩单线程带来的死锁风险。
- 改善启动小进程时的性能。

JDK 的子进程创建流程可以简化为两步：

1. 启动 helper 子进程。
2. 通过父子进程之间的 pipe 检查 helper 是否存活，以及后续 `exec` 是否成功。

在 `posix_spawn` 模式下，JDK 会让子进程在启动后先回写一个 `CHILD_IS_ALIVE` 标记。若后续 `exec` 失败，子进程会再通过 fail pipe 回传错误码。

这也解释了为什么 Java 层最终看到的是 `IOException: error=16`：这个 `16` 是子进程初始化或 `exec` 前阶段写回来的 errno。

## 第四阶段：定位到 `dup2(fail_pipe_fd, FAIL_FILENO)`

继续在 JDK native 代码中增加日志后，可以看到失败点位于：

```c
if (moveDescriptor(fail_pipe_fd, FAIL_FILENO) == -1) {
    goto WhyCantJohnnyExec;
}
```

相关实现如下：

```c
int moveDescriptor(int fd_from, int fd_to) {
    if (fd_from != fd_to) {
        if ((restartableDup2(fd_from, fd_to) == -1) ||
            (close(fd_from) == -1)) {
            return -1;
        }
    }
    return 0;
}

int restartableDup2(int fd_from, int fd_to) {
    int err;
    RESTARTABLE(dup2(fd_from, fd_to), err);
    return err;
}
```

日志显示：

```text
childProcess : restartableDup2(fd_from, fd_to) == -1
childProcess : fail_pipe_fd 496
childProcess : FAIL_FILENO 3
```

也就是说，JDK 正在尝试执行：

```c
dup2(496, 3)
```

其中：

```c
#define FAIL_FILENO (STDERR_FILENO + 1) // 3
```

`FAIL_FILENO` 固定为 3，是为了在标准输入、标准输出、标准错误之外保留一个专门用于报告 exec 失败原因的 fd。

## 第五阶段：确认 `EBUSY` 来自 Linux kernel `dup2/dup3`

Linux 中 `dup2()` 最终会进入 `dup3()` 相关逻辑，核心路径可以简化为：

```c
SYSCALL_DEFINE2(dup2, unsigned int, oldfd, unsigned int, newfd) {
    if (unlikely(newfd == oldfd)) {
        ...
    }
    return ksys_dup3(oldfd, newfd, 0);
}
```

在 `do_dup2()` 中，有一段非常关键的判断：

```c
fdt = files_fdtable(files);
tofree = fdt->fd[fd];
if (!tofree && fd_is_open(fd, fdt))
    goto Ebusy;
```

这段注释说明了一个特殊场景：目标 fd 已经被标记为 open，但对应的 `struct file` 还没有完成初始化。在这种情况下，内核无法安全地将其关闭并复用，于是返回 `-EBUSY`。

这与 JDK 日志完全吻合：

- JDK 要把 fail pipe 移动到 fd 3。
- fd 3 恰好处于被占用或半初始化状态。
- `dup2(fail_pipe_fd, 3)` 返回 `EBUSY`。
- 子进程通过 fail pipe 把 errno 16 回传给父进程。
- Java 层抛出 `IOException: error=16, Device or resource busy`。

## 第六阶段：现场确认 fd 3 被 `jemalloc` 占用

通过 `lsof -p <pid>` 检查异常进程，可以看到 fd 3 被 `jemalloc` 的 Unix domain socket 占用：

```text
java  <pid>  ...  3u  unix  ...  @jemalloc_<pid>.sock@  type=STREAM
```

而在一些正常实例中，fd 3 可能被 GC 日志文件占用：

```text
java  <pid>  ...  3w  REG  ...  /path/to/gc.log
```

差异在于：

- 普通文件 fd 可以被 `dup2()` 安全关闭并复用。
- 某些 Unix socket 在创建过程中可能处于内核认为“fd 已 open，但 file 对象尚未完成”的状态。
- 如果这个状态与 JDK 的 `dup2(..., 3)` 发生竞争，就会触发 `EBUSY`。

这也解释了为什么问题是概率性的：它依赖 fd 分配顺序、预加载库初始化时机、JDK 创建子进程时机等多个因素。

## 验证

将环境变量中的 `LD_PRELOAD=jemalloc.so` 临时移除后，`ProcessBuilder.start()` 不再复现 `EBUSY`。

这说明问题与预加载的 jemalloc 诊断/统计能力占用 fd 3 存在强相关性。

需要注意的是，移除 jemalloc 只是止损手段。它可能影响内存分配行为、内存诊断能力或线上观测能力，因此不一定适合作为长期方案。

## 修复方案演进

### 方案一：如果 jemalloc 创建 socket 得到 fd 3，则复制到其他 fd

思路是：当 jemalloc 创建 socket 后发现 fd 为 3，就通过 `fcntl` 或类似方式复制到更高编号 fd，再关闭 fd 3。

但测试发现，这种做法会延长 fd 3 的占用窗口，反而可能增加 `dup2()` 与 fd 3 竞争的概率。因此该方案不够稳妥。

### 方案二：延迟创建 jemalloc 统计 socket

思路是：延迟初始化 jemalloc 的统计服务，避免在 Java 应用启动早期过早占用 fd 3。

该方案能缓解 `ProcessBuilder.start()` 初始化阶段与 jemalloc socket 初始化之间的竞争，但并不彻底。后续仍观察到一些 shell 管道相关的 fd 复制问题，例如：

```text
cannot duplicate fd 3 to fd 8: Bad file descriptor
```

这说明仅靠“延迟创建”无法彻底消除低编号 fd 被 jemalloc 占用带来的兼容性风险。

### 最终方向：为 jemalloc 诊断服务提供显式开关

更合理的方案是：将 jemalloc 的统计/诊断 socket 作为可选能力，通过环境变量显式开启。

这样可以做到：

- 默认不创建额外 Unix socket，避免占用 fd 3 等低编号 fd。
- 需要内存诊断、火焰图或统计信息时，再显式打开。
- 降低对 JDK `posix_spawn()`、shell 管道、fd 重定向逻辑的干扰。

## 排查经验总结

这类问题容易误判为业务脚本、文件系统、机器状态或 JDK 版本问题。更可靠的排查路径是：

1. **先确认错误码来源**：Java 层的 `IOException` 不一定来自目标程序本身，也可能来自 JDK native 子进程初始化阶段。
2. **替换最小命令复现**：将 `python` 替换为 `ls`、`true` 等简单命令，可以快速排除业务脚本因素。
3. **关注 JDK 子进程创建模式**：JDK 9+ 默认 `posix_spawn()`，其行为与传统 `fork()/exec()` 不完全一致。
4. **检查低编号 fd 占用**：尤其是 fd 3，因为 OpenJDK 使用它作为 exec 失败报告通道。
5. **结合 kernel 语义理解 errno**：`EBUSY` 在 `dup2()` 中不是常见错误，但在共享 fd table 和半初始化 fd 场景下是可能出现的。
6. **警惕预加载库副作用**：`LD_PRELOAD` 注入的库如果在进程早期创建 socket、pipe、eventfd 等资源，可能改变 fd 分配顺序，并影响运行时或 shell 的假设。

## 结论

这次 `ProcessBuilder.start()` 抛出 `error=16, Device or resource busy` 的根因，是 **JDK 9+ `posix_spawn()` 子进程创建路径与预加载 jemalloc 统计 socket 在 fd 3 上发生竞争**。

从 Java 层看，它表现为启动任意外部命令失败；从 JDK native 层看，它失败在 `moveDescriptor(fail_pipe_fd, FAIL_FILENO)`；从 Linux kernel 层看，它对应 `dup2()` 尝试覆盖一个处于特殊 open 状态的目标 fd，因此返回 `EBUSY`。

短期可以通过禁用相关 `LD_PRELOAD` 能力止损；长期应避免预加载库默认占用低编号 fd，并将诊断/统计 socket 改为显式开关，降低对 JDK 子进程创建与 shell fd 重定向逻辑的影响。
