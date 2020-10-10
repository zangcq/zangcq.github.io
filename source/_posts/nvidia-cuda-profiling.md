---
title: NVIDIA CUDA PROFILING Tool
tags:
  - CUDA
  - GPU
  - profiling
id: '396'
categories:
  - - gpu-computing
    - GPGPU-Sim Notes
date: 2017-09-21 10:51:07
---

## 1\. tools

*   `nsight` in `WIN（vs）` or `Linux (eclipse）`
*   `nvprof` in `linux cmd line`
    
    ```c++
    
    //in gtx1060 
    nvprof --metrics ipc,issued_ipc,achieved_occupancy,global_hit_rate,local_hit_rate,l2_tex_read_hit_rate,gld_transactions,gst_transactions,local_load_transactions,local_store_transactions,l2_tex_read_transactions,l2_tex_write_transactions,l2_read_transactions,l2_write_transactions,dram_read_transactions,dram_write_transactions,sysmem_read_transactions,sysmem_write_transactions ./wave
    ```
    

## 2\. 度量标准 `metrics`

### 2.1 Performance

*   `ipc`
    *   Instructions executed per cycle
*   `issued_ipc`
    *   Instructions issued per cycle
*   `achieved_occupancy`
    *   Ratio of the average active warps per active cycle to the maximum number of warps supported on a multiprocessor

**说明：本文研究点在 Data Cache，那么一下的提到的`L1 Cache` 都为 `Data Cache`**

### 2.2 Cache Hit Rate

#### `L1 Cache`

**Fermi/Kepler** (Capability 2.x/3.x)

*   `l1_cache_global_hit_rate`
    *   Hit rate in `L1 cache` for global loads
*   `l1_cache_local_hit_rate`
    *   Hit rate in `L1 cache` for local loads and stores
*   `nc_cache_global_hit_rate`
    *   only for **Kepler**
    *   Hit rate in `non coherent cache` for global loads

**Maxwell/Pascal**(Capability 5.x/6.x)

*   `global_hit_rate`
    *   Hit rate for global loads
*   `local_hit_rate`
    *   Hit rate for local loads and stores

#### `L2 Cache`

**Fermi/Kepler** (Capability 2.x/3.x)

*   `l2_l1_read_hit_rate`
    *   Hit rate at `L2` cache for all read requests from `L1` cache
*   `l2_tex_read_hit_rate`
    *   Hit rate at `L2` cache for all read requests from `texture` cache

**Maxwell/Pascal**(Capability 5.x/6.x)

*   `l2_tex_read_hit_rate`
    *   Hit rate at `L2` cache for all read requests from `texture` cache

### 2.3 Transactions

#### `L1 Cache`

**Global data**

*   `gld_transactions`
    *   Number of global memory load transactions
*   `gld_transactions_per_request`
    *   Average number of global memory load transactions performed for each global memory load
*   `gst_transactions`
    *   Number of global memory store transactions
*   `gst_transactions_per_request`
    *   Average number of global memory store transactions performed for each global memory store

**Local data**

*   `local_load_transactions`
    *   Number of local memory load transactions
*   `local_load_transactions_per_request`
    *   Average number of local memory load transactions performed for each local memory load
*   `local_store_transactions`
    *   Number of local memory store transactions
*   `local_store_transactions_per_request`
    *   Average number of local memory store transactions performed for each local memory store

#### `L2 Cache`

**Fermi/Kepler** (Capability 2.x/3.x)

*   `l2_l1_read_transactions`
    *   Memory read transactions seen at `L2` cache for all read requests from `L1` cache
*   `l2_l1_write_transactions`
    *   Memory write transactions seen at `L2` cache for all write requests from `L1` cache

**Maxwell/Pascal**(Capability 5.x/6.x)

*   `l2_tex_read_transactions`
    *   Memory read transactions seen at `L2` cache for read requests from the `texture` cache
*   `l2_tex_write_transactions` **Both**
*   `l2_read_transactions`
    *   Memory read transactions seen at L2 cache for all read requests
*   `l2_write_transactions`
    *   Memory write transactions seen at L2 cache for all write requests

**Only in Kepler**

*   `nc_l2_read_transactions`
    *   Memory read transactions seen at L2 cache for non coherent global read requests

#### 备注

*   自`Kepler`架构以来，`L1 Cache` 对 `global data` 的默认策略是 `bypassing` ，只有`Fermi`架构`L1 Cache`对 global data 是既可读又可写的，但是不能保持`cache coherence` 。
*   那么为了保证 `cache coherence`,`nvidia` 采取了较为极端的做法，那就是`bypassing` `L1 Cache` ，并且在`Maxwell` 与 `Pascal` 架构中，与`Tex Cache` 合并，设置为 `Read Only` , 但我认为其效果并不佳。最新架构volta又将其架构改为 `Fermi` 中 `L1 Cache` 与 `Shared memory` 可配置的模式。

*   可知，在`Maxwell` 与 `Pascal` 架构中，我们就将 `tex cache` 看成 `L1 Data Cache`

#### `GDRAM`

*   `dram_read_transactions`
    *   Device memory read transactions
*   `dram_write_transactions`
    *   Device memory write transactions

#### `DRAM`

*   `sysmem_read_transactions`
    *   System memory read transactions
*   `sysmem_write_transactions`
    *   System memory write transactions

​ **Influence by L2 Hit Rate**

### Reference

> Read more at: [http://docs.nvidia.com/cuda/profiler-users-guide/index.html#ixzz4t4vGKod8](http://docs.nvidia.com/cuda/profiler-users-guide/index.html#ixzz4t4vGKod8) Follow us: [@GPUComputing on Twitter](http://ec.tynt.com/b/rw?id=aBENEGgL0r44W6acwqm_6r&u=GPUComputing) [NVIDIA on Facebook](http://ec.tynt.com/b/rf?id=aBENEGgL0r44W6acwqm_6r&u=NVIDIA)