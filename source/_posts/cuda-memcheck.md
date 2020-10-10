---
title: CUDA-MEMCHECK
tags:
  - CUDA
  - GPU
id: '115'
categories:
  - - programming
    - CUDA Programming
date: 2017-06-19 09:45:35
---

# CUDA-MEMCHECK

### 1.Introduction

CUDA-MEMCHECK是一个在CUDA toolkit 中的功能性的正确性检查组件。

**这个**suite有4个工具 :

#### memcheck

The memcheck tool is capable of precisely detecting and attributing out of bounds and misaligned memory access errors in CUDA applications.

在Memcheck工具能够精确检测和归因CUDA应用的出界和未对齐的内存访问错误。该工具还报告GPU所遇到的硬件例外。

#### racecheck

report shared memory data access hazards that can cause data races.

报告shared memory 的会造成data race 的数据访问错误；

#### initcheck

report cases where the GPU performs uninitialized accesses to global memory。

报告当GPU来执行为初始化的到 global memory 的访问；

#### synccheck

report cases where are application is attempting to use CTA synchronization in divergent code。

报告当应用程序试图在分歧代码里调用 CTA 同步操作的时候。

memcheck 既可以独立的安装，也可以集成在cuda toolkit 里，但是集成在cuda toolkit里的只有第一种功能。

### 2.Using CUDA-MEMCHECK

1.独立使用

$$cuda-memcheck \[options\] app\_name \[app\_options\] $$

2.在cuda gdb 使用

$$(cuda gdb) set cuda memcheck on$$

更多详见NVIDIA DOCS

> [http://docs.nvidia.com/cuda/cuda-memcheck/#about-cuda-memcheck](http://docs.nvidia.com/cuda/cuda-memcheck/#about-cuda-memcheck)