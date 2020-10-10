---
title: 数据类型 char、signed char、unsigned char 的理解
tags: []
id: '1335'
categories:
  - - programming
    - C/C++
comments: false
date: 2020-06-09 15:44:24
---

[https://stackoverflow.com/questions/75191/what-is-an-unsigned-char](https://stackoverflow.com/questions/75191/what-is-an-unsigned-char)

占坑

overview

*   表示范围
*   应用场景
*   x86跟arm服务器中默认的数据类型是什么？
    *   在迁移过程中出现的问题
    

错误实例

```
某程序以 char 作为返回值，在x86服务器上测试的时候结果正常。

但是在arm服务器上测试的时候却出现异常，程序陷入死循环

ch每次返回的都是255
```

原因分析

```
这个问题的根本原因就是gcc对于不同平台上的char类型定义不一样。

x86 上的 gcc 都把 char 定义为 signed char；
而arm64平台上使用的linux-gcc 却把 char 定义为 unsigned char 。所以造成了同样的代码在 X86 和arm平台上编译后执行的结果不一样
```

解决方法

```
对于这个来说，当然是要把 char ch 修改为 int ch ，因为这个函数本身返回的也是int 。

但是如果对于那些本来就是char类型的变量怎么办？

这里也有解决方案，这个可以参考华为之前给出的方案

1） 在编译时加-fsigned-char 参数，指定 char 为 signed char
举例： gcc -fsigned-char test.c -o test

在 Makefile 中可以使用选项 CFLAGS="-fsigned-char"、 CXXFLAGS、 CPPFLAGS 按需
添加

2）代码开发时养成良好的编程规范，使用自定义的变量类型，比如代码中定义
#define unsigned char UCHAR 或者#define signed char CHAR；这样可以跨平台


3） 修改编译器默认 char 为和 x86 的一致， 可以使用下面版本的 GCC
gcc4.9.3_signedchar.rar
```