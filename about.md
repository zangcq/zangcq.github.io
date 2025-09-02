---
layout: page
title: About
permalink: /about/
---
### About

Currently, I am a System Software Engineer at ByteDance Infrastructure,  focusing on Java workload optimization and toubleshooting.

Prior to joining ByteDance, I spent two years at [Alibaba Infrastructure Service](https://www.alibabacloud.com/).  I hold a Computer Architecture Master degree from [Shandong University](https://www.sdu.edu.cn/), where I was advised by [Lei Ju](https://faculty.sdu.edu.cn/julei).



### Project

#### ByteDance Infrastructure  Compiler and Library Group  (2020.7~Now)

#### Alibaba Infra Servive Hybrid Computing Compiler Group (2018.7 ~ 2020.7)

- Wasm AOT Compiler for Ant Blockchain Platform  (2019-2020)

  - Convert wasm bytecode to LLVM IR
  - Add T-Head CSKY Extension to the RISCV ISA
  - [资源计算方法、装置、电子设备及可读存储介质](https://www.patentguru.com/CN113296837B)   2025-02-28    ([杨岳鸣](https://www.patentguru.com/cn/inventor/3867743) [崔世强](https://www.patentguru.com/cn/inventor/3867744) [臧传奇](https://www.patentguru.com/cn/inventor/3867746)）

  - [一种程序编译方法、设备以及计算机可读介质](https://www.patentguru.com/CN113360157A)       2021-09-07  （[杨岳鸣](https://www.patentguru.com/cn/inventor/3867743) [崔世强](https://www.patentguru.com/cn/inventor/3867744) [臧传奇](https://www.patentguru.com/cn/inventor/3867746)）

- Coordinate software and hardware Optimization for CNN & DNN Accelerator implemented in FPGA  (2018-2019)
  - Implement CNN Operation like Conv/DeConv and DNN Operation like matmul/relu
  - Proposed a spliting HD pictures algorithm for Limited on-chip memory
  - Graph Optimization like Concat/Slice/Fusion

#### ShanDong Univ.  Embedded and System Labs

- [Energy Efficient Object Detection for Edge Computing](https://github.com/xiaoyuuuuu/dac-hdc-2018-object-detection-in-Jetson-TX2)
  - As project lead won [3rd place in DAC 2018 System Design Contest](http://www.cse.cuhk.edu.hk/~byu/2018-DAC-SDC/index.html）)
  - Implemented half-precision calculation on GPU
  - Network Pruning and Reduced the down sampling rate

### Paper

- NVM in GPGPU Memory Hierarchy
  - [Shared Last-level Cache Management for GPGPUs with Hybrid Main Memory](https://ieeexplore.ieee.org/abstract/document/7926953/)   (Design, Automation and Test in Europe Conference and Exhibition (DATE) 2017 [**Best Paper Award Nominations**](https://www.date-conference.com/proceedings-archive/2017/html/bestpaper.html))  Guan Wang, Xiaojun Cai,  Lei Ju, **Chuanqi Zang**, Mengying Zhao and Zhiping Jia.
  - [Shared Last-Level Cache Management and Memory Scheduling for GPGPUs with Hybrid Main Memory](https://dl.acm.org/doi/10.1145/3230643)  (ACM Trans. Embedd. Comput. Syst. (Volume 17 Issue 4, August 2018))  Guan Wang,**Chuanqi Zang**, Lei Ju, Mengying Zhao, Xiaojun Cai, and Zhiping Jia

- Cache Coherence Research in GPGPU
  - [基于编译器辅助的GPGPU缓存一致性研究](https://kns.cnki.net/KCMS/detail/detail.aspx?filename=1018107394.nh&dbname=CMFD201901&dbcode=cdmd) (Master Thesis 2018)
  - Proposed a static program analysis which enable GPU kernels to conservatively load global data in the private L1 cache which are guaranteed to have no coherence issue.
