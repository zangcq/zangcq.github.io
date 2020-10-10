---
title: NVIDIA GPU ARCH
tags:
  - CUDA
  - GPU
id: '113'
categories:
  - - programming
    - CUDA Programming
date: 2017-06-19 09:44:06
---

### Compute Capability 2.x Fermi Arch

#### Warp Scheduling

​for some warp that is ready to execute, if any. The first scheduler is in charge of the warps with an odd ID and the second scheduler is in charge of the warps with an even ID. Note that when a scheduler issues a double-precision floating-point instruction, the other scheduler cannot issue any instruction.

​A warp scheduler can issue an instruction to only half of the CUDA cores. To execute an instruction for all threads of a warp, a warp scheduler must therefore issue the instruction over two clock cycles for an integer or floating-point arithmetic instruction.

#### Cache

##### Const Cache

A multiprocessor also has a read-only constant cache that is shared by all functional units and speeds up reads from the constant memory space, which resides in device memory.

##### Data Cache

There is an L1 cache for each multiprocessor and an L2 cache shared by all multiprocessors, both of which are used to cache accesses to **local or global memory**, including temporary register spills.

The cache behavior (e.g., whether reads are cached in both L1 and L2 or in L2 only) can be partially configured on a per-access basis using modifiers to the load or store instruction.

The same on-chip memory is used for both L1 and shared memory: It can be configured as 48 KB of shared memory and 16 KB of L1 cache or as 16 KB of shared memory and 48 KB of L1 cache, using cudaFuncSetCacheConfig()/cuFuncSetCacheConfig()。

### Compute Capability 3.x Kepler Arch

#### Data cache

There is an L1 cache for each multiprocessor and an L2 cache shared by all multiprocessors. **The L1 cache is used to cache accesses to local memory, including temporary register spills.** The L2 cache is used to cache accesses to **local and global memory.** The cache behavior (e.g., whether reads are cached in both L1 and L2 or in L2 only) can be partially configured on a per-access basis using modifiers to the load or store instruction. Some devices of compute capability 3.5 and devices of compute capability 3.7 allow opt-in to caching of global memory in both L1 and L2 via compiler options.

The same on-chip memory is used for both L1 and shared memory: It can be configured as **48 KB of shared memory and 16 KB of L1 cache** or as **16 KB of shared memory and 48 KB of L1 cache** or as **32 KB of shared memory and 32 KB of L1 cache**, using cudaFuncSetCacheConfig()/cuFuncSetCacheConfig():

**Note**: Devices of compute capability 3.7 add an additional 64 KB of shared memory to each of the above configurations, yielding 112 KB, 96 KB, and 80 KB shared memory per multiprocessor, respectively. However, the maximum shared memory per thread block remains 48 KB.

### Compute Capability 5.x Maxwell Arch

##### A multiprocessor has:

*   a read-only constant cache that is shared by all functional units and speeds up reads from the constant memory space, which resides in device memory,
*   a unified L1/texture cache of 24 KB used to cache reads from global memory,
*   64 KB of shared memory for devices of compute capability 5.0 or 96 KB of shared memory for devices of compute capability 5.2.

The unified L1/texture cache is also used by the texture unit that implements the various addressing modes and data filtering mentioned in [Texture and Surface Memory](http://docs.nvidia.com/cuda/cuda-c-programming-guide/index.html#texture-and-surface-memory).

There is also an L2 cache shared by all multiprocessors that is used to cache accesses to local or global memory, including temporary register spills. Applications may query the L2 cache size by checking the l2CacheSize device property (see [Device Enumeration](http://docs.nvidia.com/cuda/cuda-c-programming-guide/index.html#device-enumeration)).