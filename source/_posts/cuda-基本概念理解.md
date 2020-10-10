---
title: CUDA 基本概念理解
tags:
  - CUDA
id: '117'
categories:
  - - programming
    - CUDA Programming
date: 2017-06-19 09:46:36
---

# CUDA 基本概念理解

**grid**

*   分配给每个kernel总的线程资源，可以是一维二维三维的，其中包含许多block。
*   共享global memory

**block**

*   grid 的组成单位，线程块嘛，分配到 GPU SM上的基本单位，不能将其拆开分到不同的SM上。
*   block内的所有线程共享 shared memory，L1 cache 。

**thread**

*   GPU线程，每个线程都有自己私有 资源，例如寄存器，local memory 等等
    
    *   ​

![](http://docs.nvidia.com/cuda/parallel-thread-execution/graphics/memory-hierarchy.png)

### 常出现在代码中几个内部变量

#### 维度

*   维度表示的总是一个方向上的总数，比如说 `blockdim.x` 就表示 在block 中，x方向上，thread的总个数。

*   `blockDim.x,y,z` gives the number of threads in a block, in the particular direction
*   `gridDim.x,y,z` gives the number of blocks in a grid, in the particular direction
*   `blockDim.x * gridDim.x` gives the number of threads in a grid (in the x direction, in this case)

#### 索引

*   索引，简单的说就是编号。比如`threadIdx.x` 这个线程在 block 中x 方向（维度）上的，一个编号，排第几

*   `threadIdx.x,y,z`
*   `blockIdx.x,y,z`

那么根据上边两个概念，我们就可以计算 在grid 中全局的 blockIdx 和 threadIdx，以及在 block 中的 threadIdx了。

比如常用的 就是在 block 中的全局threadIdx，我们假如block是三维的；

```c

tid_in_block = threadInx.x + threadIdx.y * threadDim.x + threadIdx.z *(threadDim.x * threadDim.y);
//我們可以將其想象他是一個三维数组，正好对应 xyz三维，我们想访问其中的元素的话，除了利用索引如
//a[]][][]这样的形式之外，我们也可以利用其全局的 id，就可以了。
```