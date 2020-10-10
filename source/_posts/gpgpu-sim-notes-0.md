---
title: GPGPU-Sim Notes 0
tags:
  - GPGPU-Sim
id: '270'
categories:
  - - gpu-computing
    - GPGPU-Sim Notes
date: 2017-08-07 22:47:50
---

# GPGPU-Sim 笔记整理 0

## `gpgpu-sim.cc`

本文件是所有函数的配置和初始化

*   `power_config`
*   `memory_config`
*   `shader_core_config`
*   `gpgpu_sim_config`
*   初始化模拟器
*   周期激活
*   打印状态
*   更新状态
*   死锁检查

手册解释：

Gluing different timing models in GPGPU-Sim into one. It contains implementations to support multiple clock domains and implements the

thread block dispatcher

翻译：

将GPGPU中不同的时间模型粘合成一个时间模型。其中包括了支持多个时钟域的实现和线程块调度程序的实现

这两个文件是gpgpu-sim的一个总的架构文件，相当于main函数

实现的功能

1.  将能耗、存储、核等需要的参数从gpgpusim.config中读取出来
2.  实现自己的一些方法  
    

## dram.cc

本文件为主存相关的模拟函数。

#### 存储层次

由大到小为

*   chip
*   bank
*   row
*   column

主要类

*   `dram_t`
    
*   `dram_req_t`
    
    *   row
    *   col
    *   bk
    *   `nbytes`
    *   txbytes
    *   dqbytes
    *   age
    *   timestamp 时间戳 LRU
    *   rw 判读读写
    *   addr
    *   `mem_fetch` data

### DRAM延迟参数

#### tRCD

读延迟

array read 【 】buffer read/write

between array read and buffer read/write command

#### tCL，tWL,tCCD,tWTR

限制连续的buffer 命令

独立存储单元

#### tWR，tRTP

between buffer read/write command and array read

buffer read/write 【 】 array read

#### tRP

写延迟

an array write and a following array read

array write 【】array read

#### tRRD act ，tRRD pre

限制访问频率来满足功耗预算  

only when a read evicts dirty buffer contents

#### 添加NVM的延时参数

```c++

 unsigned int RRDactc;

 unsigned int RRDprec;

 unsigned int RRDactc_PCM;

 unsigned int RRDprec_PCM;//hybrid memory structure latency paramater
```

### addrdec.cc

手册解释： Address decoder - Maps a given address to a specific row, bank, column, in a DRAM channel 翻译： 地址解码器 - 在一个DRAM channel 里 将一个给定的地址映射成 行 ，bank ，列

其中比较重要的函数 ： 1.`void linear_to_raw_address_translation::addrdec_tlx(new_addr_type addr, addrdec_t *tlx) const` 将线性地址转换成物理地址 ，地址解码转换功能 2.`void linear_to_raw_address_translation::init(unsigned int n_channel, unsigned int n_sub_partition_in_channel)` 地址转换的初始化函数，从这个函数开始，逐步调用相应的功能 3.`static new_addr_type addrdec_packbits( new_addr_type mask, new_addr_type val, unsigned char high, unsigned char low)`