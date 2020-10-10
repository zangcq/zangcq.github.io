---
title: concurrent kernel  and dynamic parallelism
tags:
  - GPU
id: '324'
categories:
  - - programming
    - CUDA Programming
date: 2017-08-12 15:48:52
---

# concurrent kernel and dynamic parallelism

## concurrent kernel

废话少说，上图 ![](https://lh3.googleusercontent.com/-FUPni3vN9zU/WQnZfyui7cI/AAAAAAAAAGM/_GwxpPx4Atk4v2SFc8ti7sJ0EBqBsfL3gCLcB/s1600/concurrent%252Bkernel%252Bexecution.png)

*   显而易见，when the source was adequate,
*   different kernel in different streams without data dependence
*   can be executing concurrent, save time and improve kernel level parallelism

## dynamic parallelism

pic ![](http://docs.nvidia.com/cuda/cuda-c-programming-guide/graphics/parent-child-launch-nesting.png)

*   引入　“父子”　概念，这个可以类似面向对象编程类的继承
*   CUDA 支持两级嵌套
*   提高性能
    *   在内核开始执行前，将内核所需的数据结构初始化。需在cpu 端做这件事
    *   可以减少递归
*   内存模型
    *   父子　kernel or grid 共享　global and constant memory
    *   各自有自己的local memory 和　shared memory
*   设备运行的时候　创建的　stream and event，只能在创建它们的线程块中使用。