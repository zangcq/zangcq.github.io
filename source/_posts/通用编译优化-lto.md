---
title: 通用编译优化-LTO
tags: []
id: '1254'
categories:
  - - uncategorized
comments: false
date: 2020-05-04 12:05:38
---

# Reference

GCC中LTO使能的例子

[http://hubicka.blogspot.com/2014/09/linktime-optimization-in-gcc-part-3.html](http://hubicka.blogspot.com/2014/09/linktime-optimization-in-gcc-part-3.html)

GCC 优化选项

[https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html](https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html)

LTO 优化的概念

[http://llvm.org/docs/LinkTimeOptimization.html#liblto](http://llvm.org/docs/LinkTimeOptimization.html#liblto)

LLVM 中的链接器，如何使能LTO

[http://llvm.org/docs/GoldPlugin.html#lto-how-to-build](http://llvm.org/docs/GoldPlugin.html#lto-how-to-build)

ThinLTO ，相当于LTO的优化版本，大大减少的链接时的时间开销

[https://clang.llvm.org/docs/ThinLTO.html#introduction](https://clang.llvm.org/docs/ThinLTO.html#introduction)

# What is LTO

**LTO**  **L**ink**T**ime **O**ptimization 

*   在 **程序链接阶段** 的优化。
*   主要优化点

*   无效Symbol的消除
*   函数的内联化
*   一些全局的优化
*   overhead

*   链接的时间会边长
*   主要是对symbol调用关系的分析
*   thinlto 对其进行了优化，做了一些tradeoff
*   GCC和Clang中都有对应优化选项

*   使用简单
*   对业务影响小
*   可以得到3~5%的纯收益
*   link cache 的存在

> [https://www.jianshu.com/p/58fef052291a](https://www.jianshu.com/p/58fef052291a)