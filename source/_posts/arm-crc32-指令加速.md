---
title: ARM CRC32 指令加速
tags: []
id: '1300'
categories:
  - - 通用编译技术
comments: false
date: 2020-05-17 17:00:01
---

## CRC32是什么？

*   A cyclic redundancy check 32(CRC32)
*   32 位的循环冗余检查
*   第一次接触是在计算机网络的课上，用于**网络传输**的数据校验
*   工作上是在数据库这种**数据存储**的场景

功能与性能

*   从其检错能力来看，它所不能发现的错误的几率仅为0.0047%以下。
*   从性能上和开销上考虑，均远远优于[奇偶校验](https://baike.baidu.com/item/%E5%A5%87%E5%81%B6%E6%A0%A1%E9%AA%8C)及算术和校验等方式。

*   [https://baike.baidu.com/item/CRC/1453359](https://baike.baidu.com/item/CRC/1453359)
*   [https://baike.baidu.com/item/CRC32](https://baike.baidu.com/item/CRC32)

CRC算法原理

![](https://bkimg.cdn.bcebos.com/pic/a50f4bfbfbedab64928a2448f036afc378311eb9?x-bce-process=image/watermark,g_7,image_d2F0ZXIvYmFpa2U2MA==,xp_5,yp_5)

*   D（数据） 是一个待校验的长度为 k 的比特t流
*   数据D后添加(n-k)比特冗余位(又称帧检验序列，Frame Check Sequence，FCS)
*   形成n比特的传输帧T，再将其发送出去。

*   循环冗余校验提供一个预先设定的(n-k+1)比特整数P，
*   并且要求添加的(n-k)比特F满足：**T mod P == 0** （T对P取余=0）
*   **其中 T =2n-kD + F** （D左移n-k 位 + F）

基于上述要求，实际应用时，发送方和接收方按以下方式通信：

1\. 发送方和接收方在通信前，约定好预设整数P。

2\. 发送方在发送前根据数据D确定满足(1)式的F，生成CRC码 T，T 即为数据位D与校验位F的拼接，发送T。

3\. 接收方收到CRC码 T，进行 result = T mod P 运算，当且仅当result = 0时接收方认为没有差错。

模二运算采用无进位的二进制加法，恰好为异或(XOR)操作

*   **F **\=**2n-kD mod P**eg
*   P=1010 （自己编的）
*   D=1100
*   **F**\= **1100 000** mod **1010** \= 110
*   T=1100 110

CRC的本质是模-2除法的余数，采用的除数不同，CRC的类型也就不一样。通常，CRC的**除数用生成多项式来表示**。最常用的CRC码的生成多项式如表1所示。最常用的CRC码及生成多项式名称生成多项式

**自定义除数**

![](http://www.zangcq.com/wp-content/uploads/2020/05/image-1-1024x426.png)

## 查看 ARM 硬件支持

![](http://www.zangcq.com/wp-content/uploads/2020/05/image-1024x188.png)

cat /proc/cpuinfo

如果对应feature 存在，那么就可以使用了crc32硬件指令加速，编译器的作用，实际上就是一个enable 硬件feature的过程。

## 使能CRC32 ARM Instruction

https://www.jiangwei.org/2016/04/25/armv8-crc32%E6%8C%87%E4%BB%A4%E9%9B%86%E6%B5%8B%E8%AF%95/

android 实现：[https://blog.csdn.net/lyx2007825/article/details/77113256](https://blog.csdn.net/lyx2007825/article/details/77113256)

添加 intrinsic

d 代表 double ：\_\_crc32cd: 一次完成8个Byte的CRC32C计算，对应crc32cx指令。

w 代表 word ：\_\_crc32cw：一次完成4个Byte的CRC32C计算，对应crc32cw指令。

h 代表 half： \_\_crc32ch：一次完成2个Byte的CRC32C计算，对应crc32ch指令。

b 代表 byte：\_\_crc32cb: 一次完成1个Byte的CRC32C计算，对应crc32cb指令。

添加对应编译选项

\-mcpu=cortex-a72+crc
-mcpu=generic+crc

difference of CRC32 and CRC32C

*   F 取值不一样
    *   CRC32 ： 0x04C11DB7; its reversed form 0xEDB88320
    *   CRC32C (0x1EDC6F41, reversed 0x82F63B78)
*   CRC32 在Intel CPU 上，有加速效果，本来3 cycle 计算 32bit，现在一个cycle就可以完成。

[https://stackoverflow.com/questions/26429360/crc32-vs-crc32c](https://stackoverflow.com/questions/26429360/crc32-vs-crc32c)