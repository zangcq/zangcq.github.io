---
title: gdb调试正在运行的进程
tags: []
id: '1258'
categories:
  - - 工欲善其事必先利其器
comments: false
date: 2020-05-04 12:08:33
---

#### 1\. gdb调试正在运行的进程

GDB可以对正在执行的程序进行调度，它允许开发人员中断程序 并查看其状态，之后还能让这个程序正常地继续执行

(gdb) attach xxxxx --- xxxxx为利用ps命令获得的子进程process id
(gdb) stop --- 这点很重要，你需要先暂停那个子进程，然后设置一些断点和一些Watch
(gdb) break 37 -- 在result = wib(value, div);这行设置一个断点,可以使用list命令察看源代码
Breakpoint 1 at 0x10808: file eg1.c, line 37.
(gdb) continue
Continuing.
Breakpoint 1, main () at eg1.c:37
37                              result = wib(value, div);
(gdb) step

在完成调试之后，不要忘记用detach命令断开连接，让被调试的进程可以继续正常运行。

我们可以通过  1)  gdb prog\_name -> r               用在逐步调试自己的程序时
            2)  gdb -> attach process\_id       正在运行中的后台程序突然卡在了某个地方，先ps再gdb/attach

            3)  gdb prog\_name core              程序core掉了

三种方式对一个程序进行调试；

#### 2\. thread——gdb 多线程调试命令

info threads:           显示当前进程中的线程；

thread thread\_no:  进入线程xx，通常紧接而来的是 bt/f 命令；

#### 3\. strace/ltrace

前者关注系统调用和程序所接收的信号；后者关注库函数调用；

strace的应用在 我们没有程序的源码，或者不方便从头开始运行程序时；可以方便查看一个应用程序进行了哪些系统调用。

而在希望知道程序都调用了动态库中的哪些函数时，我们使用 ltrace。ltrace有个-S选项，类似于strace功能。

#### 4.检查内存泄漏的工具

valgrind (in linux, free)

visual leak detector (windows , free)

boundschecker(windows, free)

profile工具：

oprofile

vtune

perf