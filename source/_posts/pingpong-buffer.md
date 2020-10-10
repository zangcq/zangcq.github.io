---
title: PingPong buffer
tags: []
id: '1009'
categories:
  - - 程序人生
comments: false
date: 2019-11-05 17:36:05
---

##### Overview

加速器常用流水的流水buffer；

*   PingPong buffer 是一个拥有两块相同大小存储的Buffer
*   用来在数据处理时掩盖 IO操作（Read/Write）

借用这个图来说明一下：

我们先定义上一部分为 ping；下一部分为pong

![](http://www.scicompiler.cloud/userguide/lib/Cattura1.png)

1.  一块buffer（灰色部分）用来存储 较为 旧的数据；用来User Process的读取
2.  另一块来 接受 IO Device的写的新数据；
3.  现在Ping作为IO的consumer；Pong 作为 User Process 的 producer；

当Pong的数据 被 User Process 用完时，那么他就可以标记为可写了；那么此时Ping的数据就作为 User Process的 producer 了；然后Pong作为新数据的接受buffer；如此就可以边读边写，流水起来了

##### Reference

[http://www.scicompiler.cloud/userguide/PingPongBuffer.html](http://www.scicompiler.cloud/userguide/PingPongBuffer.html)