---
title: GPGPU-Sim Notes —— Cache
tags:
  - Cache
  - GPU
id: '219'
categories:
  - - gpu-computing
    - GPGPU-Sim Notes
date: 2017-07-24 15:22:14
---

# GPGPU-Sim笔记整理 cache

## gpgpu-cache.cc

本文件主要分为三部分：

一；tag array

二；MSHR

三；CACHE

**.h文件**

主要定义了

#### 枚举类型

名称

定义

内容

cache\_block\_state

定义cache行的状态

INVALID（无效的）,RESERVED（保留） VALID（有效）,MODIFIED（修改的，dirty）

cache\_request\_status

cache请求的状态

HIT/MISSHIT\_RESERVED(命中保留，表示数据在L2 -INCT队列中)RESERVATION\_FAIL

cache\_event

访问cache的事件

WRITE\_BACK\_REQUEST\_SENT,写回请求READ\_REQUEST\_SENT, 读请求WRITE\_REQUEST\_SENT 写请求

replacement\_policy\_t

cache 替换策略

LRU, FIFO,

write\_policy\_t

cache 写策略

READ\_ONLY, 只读 WRITE\_BACK, 写回 WRITE\_THROUGH,写直达 WRITE\_EVICT, 写剔除 LOCAL\_WB\_GLOBAL\_WT 局部写回 全局写直达

allocation\_policy\_t

分配策略在miss时，是否将数据填入cache。

ON\_MISS, 不将数据填入cache ON\_FILL 将数据填入cache

mshr\_config\_t

MSHR 的配置方法

TEX\_FIFO,用于texture（纹理cache）ASSOC//用于普通cache

set\_index\_function

用于set 索引号的方法

FERMI\_HASH\_SET\_FUNCTION = 0,费米哈希设置 LINEAR\_SET\_FUNCTION, 线性设置 CUSTOM\_SET\_FUNCTION ？？？？？

#### 结构体

cache\_block\_t

cache块结构

new\_addr\_type m\_tag; new\_addr\_type m\_block\_addr; unsigned m\_alloc\_time; unsigned m\_last\_access\_time; unsigned m\_label; unsigned m\_eacnt; unsigned m\_lru; unsigned m\_fill\_time; cache\_block\_state m\_status;

cache\_sub\_stats

cache统计信息

accessmisspending hitreservation

extra\_mf\_fields

在data\_cache 类的在texture\_cachel类中也有不知道啥意思

bool m\_valid; new\_addr\_type m\_block\_addr; unsigned m\_cache\_index; unsigned m\_data\_size;

fragment\_entry

texture\_cache

mem\_fetch \*m\_request; // request informationunsigned m\_cache\_index; where to look for databool m\_miss; // true if sent memory requestunsigned m\_data\_size;

rob\_entry

texture\_cache

bool m\_ready;unsigned m\_time; // which cycle did this entry become ready?unsigned m\_index; // where in cache should block be placed?mem\_fetch \*m\_request;new\_addr\_type m\_block\_addr;

data\_block

texture\_cache

bool m\_valid; new\_addr\_type m\_block\_addr;

extra\_mf\_fields

texture\_cache

bool m\_valid; unsigned m\_rob\_index;

#### tag\_array()  

类名

描述

重点说明

cache\_config

cache配置的类

主要作用是初始化cache；读取配置文件gpgpu.config中的参数重要函数init()：读入配置参数，初始化cacheset\_index():设置cache块索引tag（）：读取tag位

l1d\_cache\_configl2\_cache\_config

继承cache\_config

tag\_array

详见cache基础

重要函数;probe():查找cache中的块实现LRU策略access():实现cache 策略的主要功能函数fill（） 实现对cache的填充flush（）冲刷，清空

mshr\_table

MSHR表，用来存放miss轨迹的

重要函数：probefulladd

cache\_stats

cache统计信息的类

主要统计cache的访问次数，命中率利用率等等

cache\_t

所有cache的父类

继承关系详见cache继承关系

baseline\_cache

1.理解一下cache结构tag  

For generality, the tag includes both index and tag. This allows for more complex set index calculations that can result in different indexes mapping to the same set, thus the full tag + index is required to check for hit/miss. Tag is now identical to the block address.  

tag（标记字段）通常包括index（索引）和tag（标记）。这样允许我们设置更复杂的索引计算，会导致不同的索引映射到同一个set（cache存储单元）里，因此满的 tag+index 需要进行检查是否命中。现在tag和block地址是相同的。  

#### cache 继承关系

![](https://zangcq.me/wp-content/uploads/2017/11/cache.png)