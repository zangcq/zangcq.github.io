---
title: gdb常用技巧
tags: []
id: '684'
categories:
  - - 工欲善其事必先利其器
date: 2018-11-29 21:32:22
---

### 进入gdb

```shell
gdb ./a.out
gdb -args python a.py
gdb -args sh run.sh
```

### 断点操作

1.  打断点
    
    ```shell
    # file:line number
    b a.cc:10
    # 函数入口
    b func()
    ```
    
2.  查看断点信息，有几个断点
    
    `info b`
    
3.  断点其他操作
    
    *   delete 断点号n：删除第n个断点
    *   disable 断点号n：暂停第n个断点
    *   enable 断点号n：开启第n个断点
    *   clear 行号n：清除第n行的断点
    *   delete breakpoints：清除所有断点

### 运行相关

*   run：简记为 r
    
    其作用是运行程序，当遇到断点后，程序会在断点处停止运行，等待用户输入下一步的命令。
    
*   continue （简写c ）
    
    继续执行，到下一个断点处（或运行结束）
    
*   next：（简写 n）
    
    单步跟踪程序，当遇到函数调用时，也**不进入此函数体**；此命令同 step 的主要区别是，step 遇到用户自定义的函数，将步进到函数中去运行，而 next 则直接调用函数，不会进入到函数体内。
    
*   step （简写s）
    
    单步调试如果有函数调用，则**进入函数**；与命令n不同，n是不进入调用的函数的
    
*   until
    
    当你厌倦了在一个循环体内单步跟踪时，这个命令可以运行程序直到退出循环体。
    
*   until+行号
    
    运行至某行，不仅仅用来跳出循环
    
*   finish
    
    运行程序，**直到当前函数完成返回**，并打印函数返回时的堆栈地址和返回值及参数值等信息。
    
*   call 函数(参数)
    
    **调用程序中可见的函数，并传递“参数”**，如：call gdb\_test(55)
    
*   quit：简记为 q ，**退出gdb**
    

### 打印信息

*   print 表达式：简记为 p ，
    
    其中“**表达式**”可以是任何当前正在被测试程序的有效表达式，比如当前正在调试C语言的程序，那么“表达式”可以是任何C语言的有效表达式，包括数字，变量甚至是函数调用
    
    ```shell
    # 打印某个值
    p input[0]
    
    # 打印从input[0]开始后连续1000个值，用于数组或者vector等
    p input[0]@1000
    
    # 取某个地址中的值
    p *((float *)0x112316)
    
    # 善于利用指针 
    (gdb) p input
    $1 = {0x7ffff7f86010, 0x7ffff7ef5010, 0x67f0b0, 0x7ffff7e64010, 0x6500f0, 0x7ffff7e2d010, 0x64fbf0, 0x6517c0, 0x690680}
    # 善于利用强制转换
    (gdb) p index
    $60 = 140737339105376
    (gdb) p (int)index
    $61 = -149249952
    ```
    
*   print gdb\_test(a)：
    
    将以**变量 a 作为参数调用** gdb\_test() 函数
    
*   display 表达式
    
    在单步运行时将非常有用，使用display命令设置一个表达式后，它将在每次单步进行指令后，紧接着**输出被设置的表达式及值**。如： display a
    
*   watch 表达式
    
    设置一个监视点，一旦被**监视的“表达式”的值改变**，gdb将强行终止正在被调试的程序。
    
    ```shell
    watch *(void **) 0x647a40
    ```
    
*   whatis ：查询变量或函数
    
*   info function： 查询函数
    
*   扩展info locals： 显示当前堆栈页的所有变量
    

### 查询运行信息

*   where/bt ：当前运行的堆栈列表；
*   bt backtrace 显示当前调用堆栈
*   up/down 改变堆栈显示的深度
*   set args 参数:指定运行时的参数
*   show args：查看设置好的参数
*   info program： 来查看程序的是否在运行，进程号，被暂停的原因

### 分割窗口

*   layout：用于分割窗口，可以一边查看代码，一边测试：
*   layout src：显示源代码窗口
*   layout asm：显示反汇编窗口
*   layout regs：显示源代码/反汇编和CPU寄存器窗口
*   layout split：显示源代码和反汇编窗口
*   Ctrl + L：刷新窗口

> [https://linuxtools-rst.readthedocs.io/zh\_CN/latest/tool/gdb.html](https://linuxtools-rst.readthedocs.io/zh_CN/latest/tool/gdb.html)