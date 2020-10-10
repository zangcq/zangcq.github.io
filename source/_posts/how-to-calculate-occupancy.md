---
title: How to calculate occupancy
tags:
  - CUDA
id: '379'
categories:
  - - programming
    - CUDA Programming
date: 2017-08-24 23:31:28
---

## How to calculate occupancy

这个问题，其实之前模模糊糊看到 过，只看到了定义，然后没有去深究，正好前几天面试被问到的了，总结一下吧。

### 0\. 基本概念

software

`thread` 线程

`*warp` 线程束

英文翻译出来是 歪曲，经纱，绞船索。

那么其实经纱已经很形象了，我们thread想象成每根线，那么多根线绑起来不就是经纱吗？

一簇 32根 线 的经纱。

`block` 线程块

`grid` 线程网格

hardware

`sp` Streaming Processor 类似于cpu中的ALU？

`sm` Streaming Multiprocessor 类似于CPU中的一个CORE

`gpu`（device）

`cpu` （host）

### 1.定义 What is occupancy

原文

There is a maximum number of warps which can be concurrently active on a Streaming Multiprocessor (SM), as listed in [the Programming Guide's table of compute capabilities](http://docs.nvidia.com/cuda/cuda-c-programming-guide/index.html#compute-capabilities). Occupancy is defined as the ratio of active warps on an SM to the maximum number of active warps supported by the SM. Occupancy varies over time as warps begin and end, and can be different for each SM.

CUDA编程手册里解释说，在每种计算能力不同的架构中，在SM中最大 活跃的warp的数量，occupancy 就是一个比值，`active warps / maximum active warps`，每段时间的`occupancy` 和每个 SM上的都不同。

1.5 影响 `occupancy` 的因素及优化

这个先空着吧，有空写上

### 2.计算 CUDA Occupancy Calculator

#### 1.计算器

[http://developer.download.nvidia.com/compute/cuda/CUDA\_Occupancy\_calculator.xls](http://developer.download.nvidia.com/compute/cuda/CUDA_Occupancy_calculator.xls)

这个excel 文件就是 计算器。具体使用方法都在help里边，用到的时候就仔细看看。

这个文件内容很多，每个架构的各种参数都很细。从 sm\_20到sm\_\_62都有。

#### 2.profile工具

直接在nsight （vs 或 eclipse）中可以得到，或者nvprof

### 3.参考 Reference

1.achieved occupancy in nsight

> [http://docs.nvidia.com/gameworks/content/developertools/desktop/analysis/report/cudaexperiments/kernellevel/achievedoccupancy.htm](http://docs.nvidia.com/gameworks/content/developertools/desktop/analysis/report/cudaexperiments/kernellevel/achievedoccupancy.htm)

2.basic gpu performance

> [https://www.cs.utexas.edu/](https://www.cs.utexas.edu/)~pingali/CS378/2015sp/lectures/BasicGPUPerformance.pdf

3.cuda warps and occupancy

> [http://developer.download.nvidia.com/CUDA/training/cuda\_webinars\_WarpsAndOccupancy.pdf](http://developer.download.nvidia.com/CUDA/training/cuda_webinars_WarpsAndOccupancy.pdf)