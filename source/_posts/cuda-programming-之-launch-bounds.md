---
title: CUDA Programming 之 Launch Bounds
tags:
  - CUDA
  - GPU
id: '232'
categories:
  - - programming
    - CUDA Programming
date: 2017-07-30 22:29:48
---

# [Launch Bounds](http://docs.nvidia.com/cuda/cuda-c-programming-guide/index.html#launch-bounds)

## 1.概述

As discussed in detail in Multiprocessor Level, the fewer registers a kernel uses, the more threads and thread blocks are likely to reside on a multiprocessor, which can improve performance.

在SM上驻留的线程和TB（thread block）越多，其性能就越高。第一句我不是很明白，kernel函数用的寄存器越少，同样能提升性能。我反而觉得，寄存器作为线程私有资源，每个线程分配的越多越好，launch bound可以限制每个SM上的最多线程数，同时也限制了寄存器的使用吧。

## 2.用法

### 2.1概要

Therefore, the compiler uses heuristics to minimize register usage while keeping register spilling (see[Device Memory Accesses](http://docs.nvidia.com/cuda/cuda-c-programming-guide/index.html#device-memory-accesses)) and instruction count to a minimum. An application can optionally aid these heuristics by providing additional information to the compiler in the form of launch bounds that are specified using the `__launch_bounds__()`qualifier in the definition of a `__global__`function:

其用法就是在kernel函数，来做一些限制。

```c

__global__ void launch_bounds(maxThreadsPerBlock, minBlocksPerMultiprocessor)

MyKernel(...)
{
  ....
}
```

### 2.2参数

*   `maxThreadsPerBlock`specifies the maximum number of threads per block with which the application will ever launch `MyKernel()`; it compiles to the `.maxntid`PTX directive;
*   每个 CTA 中 最大的线程数。
*   `minBlocksPerMultiprocessor` is optional and specifies the desired minimum number of resident blocks per multiprocessor; it compiles to the `.minnctapersm`PTX directive.
*   每个SM上最小的CTA数。驻留数

## 3.分析

If launch bounds are specified, the compiler first derives from them the upper limit _L_ on the number of registers the kernel should use to ensure that `minBlocksPerMultiprocessor`blocks (or a single block if `minBlocksPerMultiprocessor` is not specified) of `maxThreadsPerBlock` threads can reside on the multiprocessor (see Hardware Multithreading for the relationship between the number of registers used by a kernel and the number of registers allocated per block).

还是接前文所说，如果`lanch baund`定义好了，那么编译器就会产生一个限制值L；这个L其实就是寄存器的可使用的数量，从而确保了上边两个参数的大小。

The compiler then optimizes register usage in the following way:

*   If the initial register usage is higher than L, the compiler reduces it further until it becomes less or equal to L, usually at the expense of more local memory usage and/or higher number of instructions;
    
*   如果寄存器的使用量比L高，那么编译器会将其减少到小于或者等于L；通常要消耗更多local memory
    
*   If the initial register usage is lower than L
    
    *   If `maxThreadsPerBlock` is specified and`minBlocksPerMultiprocessor` is not, the compiler uses `maxThreadsPerBlock` to determine the register usage _thresholds_ for the transitions between n and n+1 resident blocks (i.e., when using one less register makes room for an additional resident block as in the example of Multiprocessor Level) and then applies similar heuristics as when no launch bounds are specified;
        
        *   当只定义了maxThreadsPerBlock时，编译器会通过其决定 寄存器的阈值（上限）并且当这两个参数都没有确定时，编译器会应用启发式算法来确定寄存器的使用情况。
    *   If both `minBlocksPerMultiprocessor` and`maxThreadsPerBlock` are specified, the compiler may increase register usage as high as L to reduce the number of instructions and better hide single thread instruction latency.
        
        *   当两个参数都确定之后，编译器会尽可能的将寄存器的利用率提高到 L，，减少指令数量来更好的隐藏单线程指令的延迟。

A kernel will fail to launch if it is executed with more threads per block than its launch bound `maxThreadsPerBlock.`

如果kernel 函数 执行了多于maxThreadsPerBlock的thread数的话，，会启动失败。

### 4.Example

Optimal launch bounds for a given kernel will usually differ across major architecture revisions. The sample code below shows how this is typically handled in device code using the`__CUDA_ARCH__` macro introduced in Application Compatibility

```c

#define THREADS_PER_BLOCK      256
#if CUDA_ARCH >= 200
#define MY_KERNEL_MAX_THREADS  (2 * THREADS_PER_BLOCK)
#define MY_KERNEL_MIN_BLOCKS   3
#else
#define MY_KERNEL_MAX_THREADS  THREADS_PER_BLOCK
#define MY_KERNEL_MIN_BLOCKS   2
#endif
// Device code
__global_ void
launch_bounds(MY_KERNEL_MAX_THREADS, MY_KERNEL_MIN_BLOCKS)

MyKernel(...)
{}
```

通常根据体系架构的不同，会对`launch bounds`进行优化，因为fermi，Kepler，Maxwell以及pascal其架构都有所不同，每个SM上的寄存器数量也不一样。因此这个例子呢，就是根据架构来设计不同的参数值。

In the common case where `MyKernel` is invoked with the maximum number of threads per block (specified as the first parameter of `__launch_bounds__()`), it is tempting to use `MY_KERNEL_MAX_THREADS` as the number of threads per block in the execution configuration:

```c

// Host code
MyKernel<<<blocksPerGrid, MY_KERNEL_MAX_THREADS>>>(...);
```

This will not work however since `__CUDA_ARCH__` is undefined in host code as mentioned in Application Compatibility, so `MyKernel` will launch with 256 threads per block even when `__CUDA_ARCH__`is greater or equal to 200. Instead the number of threads per block should be determined:

Either at compile time using a macro that does not depend on`__CUDA_ARCH__`, for example

```c

// Host code
MyKernel<<<blocksPerGrid, THREADS_PER_BLOCK>>>(...);
```

Or at runtime based on the compute capability

```c

// Host code
cudaGetDeviceProperties(&deviceProp, device);
int threadsPerBlock =(deviceProp.major >= 2 ? 2 * THREADS_PER_BLOCK : THREADS_PER_BLOCK);
MyKernel<<<blocksPerGrid, threadsPerBlock>>>(...);
```

### 5.Register usage

Register usage is reported by the `--ptxas`options`=-v`compiler option. The number of resident blocks can be derived from the occupancy reported by the CUDA profiler (see Device Memory Accessesfor a definition of occupancy).

Register usage can also be controlled for all`__global__` functions in a file using the `maxrregcount`compiler option. The value of `maxrregcount` is ignored for functions with launch bounds.

其实寄存器利用率也有专门的编译选项，但是当`launch bounds`确定之后，就会被忽略。。