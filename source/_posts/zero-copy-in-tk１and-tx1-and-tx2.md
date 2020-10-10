---
title: Zero copy in TK1 and TX1 and TX2
tags:
  - GPU
id: '330'
categories:
  - - gpu-computing
    - Jetson TX1-2
date: 2017-08-12 17:17:27
---

# Zero copy in TK１and TX1 and TX２

## tx1 架构图

![这里写图片描述](http://zangcq.me/wp-content/uploads/2017/08/TX1_ARCH.png)

### 说明

1.  JETSON TK1,TX1,TX2都是CPU-GPU异构架构，共享主存DRAM(最下边的)
2.  左上角，四核arm A57
3.  下一个，四核arm A53
4.  右边GPU 双核Maxwell arch sm_53 /TX 2 是pascal arch sm_62
5.  缓存各管各的，无共享 last level cache

## 零拷贝问题

*   这个技术其实提出的很早（~2009），但是走的PCI-e,类似与将数据从内存映射到显存
    
*   那么对于TX1这类统一主存的架构既可以使用传统的拷贝，也可以使用零拷贝的技术
    
    *   传统方法，那么依然是另开辟内存，做一个备份，那么GPU只访问这块儿数据。
        
    *   零拷贝技术，其实就是GPU直接访问主存，指针相同。
        
        *   but GPU 的cache 就不能用了，无论L1 还是 L2 。
        *   Cache Coherence 所致,一想就知道有多复杂。。
*   零拷贝后的性能一定会好吗
    
    *   NVIDIA 技术人员直接回复，第一句话就是 大家被这篇文章《Zero Copy on Tegra K1》误导了。下边是原话
    *   Regarding the article [http://arrayfire.com/zero-copy-on-tegra-k1/](http://arrayfire.com/zero-copy-on-tegra-k1/) from 2014 stating that zero-copy is faster than cudaMalloc, this article is mis-leading and generalizes the zero-copy case. This is not really accurate.　不是很准确
    *   Zero copy is only faster in some cases where the access pattern does not benefit from caches.
    *   Zero-Copy memory on Tegra is CPU and GPU uncached. So every access by the CUDA kernel goes to DRAM. So if the kernel repeatedly accesses the same memory location from then it is likely that the cudaMalloc memory is faster.
    
    但是那篇文章的例子不错，流数据类型应用，对于cache 并不敏感。因此效果好。
    
    借鉴一下那篇文章的总结对于零拷贝和传统的拷贝方法。
    
*   只有这个青岛小哥看到了事情的两面性,赞一个
    
    *   [http://s1nh.org/post/tx-1-zero-copy/](http://s1nh.org/post/tx-1-zero-copy/)

### 传统模式

```c++

//代码写的挺舒服的，
// Host Arrays
float* h_in  = new float[sizeIn];
float* h_out = new float[sizeOut];
 
//Process h_in
 
// Device arrays
float *d_out, *d_in;
 
// Allocate memory on the device
cudaMalloc((void **) &d_in,  sizeIn ));
cudaMalloc((void **) &d_out, sizeOut));
 
// Copy array contents of input from the host (CPU) to the device (GPU)
cudaMemcpy(d_in, h_in, sizeX * sizeY * sizeof(float), cudaMemcpyHostToDevice);
 
// Launch the GPU kernel
kernel<<<blocks, threads>>>(d_out, d_in);
 
// Copy result back
cudaMemcpy(h_out, d_out, sizeOut, cudaMemcpyDeviceToHost);
// Continue processing on host using h_out
```

### 零拷贝模式

```c++

// 1.Set flag to enable zero copy access 设置零拷贝标志
cudaSetDeviceFlags(cudaDeviceMapHost);
 
// Host Arrays
float* h_in  = NULL;
float* h_out = NULL;
 
// Process h_in
 //2.分配主机内存
// Allocate host memory using CUDA allocation calls
cudaHostAlloc((void **)&h_in,  sizeIn,  cudaHostAllocMapped);
cudaHostAlloc((void **)&h_out, sizeOut, cudaHostAllocMapped);
 
// Device arrays
float *d_out, *d_in;
// ３．共用指针呗，，反正缓存也用不了了２３３３
// Get device pointer from host memory. No allocation or memcpy
cudaHostGetDevicePointer((void **)&d_in,  (void *) h_in , 0);
cudaHostGetDevicePointer((void **)&d_out, (void *) h_out, 0);
 
// Launch the GPU kernel
kernel<<<blocks, threads>>>(d_out, d_in);
// No need to copy d_out back
// Continue processing on host using h_out
```

这个使用方法总结的不错。。。。

### reference

*   nvidia 社区讨论
    
    > [https://devtalk.nvidia.com/default/topic/922626/jetson-tx1/regarding-usage-of-zero-copy-on-tx1-to-improve-performance/](https://devtalk.nvidia.com/default/topic/922626/jetson-tx1/regarding-usage-of-zero-copy-on-tx1-to-improve-performance/)
    
*   rtas17
    
    > An Evaluation of the NVIDIA TX1 for Supporting Real-time Computer-Vision Workloads
    

*   青岛小哥
    
    > [http://s1nh.org/post/tx-1-zero-copy/](http://s1nh.org/post/tx-1-zero-copy/)
    

*   Zero Copy on Tegra K1
    
    > [http://arrayfire.com/zero-copy-on-tegra-k1/](http://arrayfire.com/zero-copy-on-tegra-k1/)