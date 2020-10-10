---
title: undefine reference 问题
tags: []
id: '1337'
categories:
  - - programming
    - C/C++
comments: false
date: 2020-06-09 17:05:59
---

> [https://blog.csdn.net/lovemysea/article/details/79520516](https://blog.csdn.net/lovemysea/article/details/79520516)
> 
> csdn 博客

> [https://stackoverflow.com/questions/5526461/gcc-warning-function-used-but-not-defined](https://stackoverflow.com/questions/5526461/gcc-warning-function-used-but-not-defined)
> 
> static 用法说明

最近在做提取热点函数的工作，也是写了类似于reference 1 中的demo 函数，将其从main.c中拆解开来。当我按照\[1\]中做法搞定时，仍然出现\`undefined reference\` 的问题，就是说，在.o文件链接阶段，仍然没有找到对应的符号（函数名 symbol）。

经过排查，我将那个要用的函数 使用了 static 进行声明，而static关键字又限制了这个函数的使用范围，仅限在.c 文件中。因此我在main.c中，就无法链接到它了。

这里我们可以看到一点，就是如果为了安全或者私有性，我们可以使用static关键字来进行限定。如果我们又需要在其他文件中调用这个func，那么就将static去掉，或者使用extern 关键字。