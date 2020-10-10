---
title: TensorRT 学习
tags: []
id: '790'
categories:
  - - GPGPU
date: 2019-05-12 15:00:50
---

> [https://mp.weixin.qq.com/s/F\_VvLTWfg-COZKrQAtOSwg](https://mp.weixin.qq.com/s/F_VvLTWfg-COZKrQAtOSwg)

### TensorRT 5 （15 min）

*   支持turing 架构 **T4** 新的硬件特性，有相应的支持。
*   MPS 继承 Volta
*   INT8 量化 （开放在API list中）10.25 release

### CUDA 10 （1h15min）

*   支持turing 架构
*   CUDA Graph
    *   目的增加并行度
    *   stream 串行相对比
    *   可以包含 cpu call back ，多gpu的支持
*   NVCC 新选项 -ewp
    *   cpu gpu lib
*   cuda 与 driver 的兼容问题
    *   本来是一一对应的关系
    *   现在cuda 10 可以在 384 运行，但是要手动添加 lib.so ( 3个 )
*   NVIDIA GPU CLOUD
    *   阿里云上应用
    *   Container 无需自己搭建环境
    *   支持各种framework
    *   free
*   cuFFT / cuBLAS / cuSOLVER /nvJPEG( Decode ) /CUTLASS
    *   各种库的支持
*   Developer Tools NSIGHT
    *   增加了许多新特性的支持
    *   完备性增强
*   warp 的independent的特性
    *   从Volta`开始支持`