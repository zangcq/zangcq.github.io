---
icon: fas fa-info-circle
order: 5
lang: en
lang-exclusive: ["en"]
page_id: about
---
Currently, I am a System Software Engineer at ByteDance Infrastructure, focusing on Java workload optimization and troubleshooting.

Prior to joining ByteDance, I spent two years at [Alibaba Infrastructure Service](https://www.alibabacloud.com/). I hold a Computer Architecture Master degree from [Shandong University](https://www.sdu.edu.cn/), where I was advised by [Lei Ju](https://faculty.sdu.edu.cn/julei).

### Project

#### ByteDance Infrastructure | Compiler and Library Group (2020.7~Now)

- ByteDance OpenJDK Tech Lead
  - Self-build OpenJDK binaries at ByteDance; provide base Docker images and datacenter JDK deployment.
  - Led the company-wide JDK 8 to JDK 17 upgrade for big data services, deployed at a scale of 10M+ cores.
  - Deep understanding of GC, JIT and the runtime system; experienced in troubleshooting memory leaks and coredumps.
- Analyzed datacenter workloads in depth and delivered optimization solutions.
  - Designed and implemented a G1 elastic heap solution, strengthening the vertical scaling capability of services.
  - Designed and implemented transparent huge pages for CodeCache and LibJVM, improving the iTLB cache hit rate.
  - Deeply involved in the bring-up and performance tuning of x86, ARM and RISC-V servers.

#### Alibaba Infra Service | Hybrid Computing Compiler Group (2018.7 ~ 2020.7)

- Wasm AOT Compiler Framework for Ant Blockchain Platform (2019.9-2020.6)
  - Convert wasm bytecode to LLVM IR and Add T-Head CSKY Extension to the RISCV ISA
  - [一种程序编译方法、设备以及计算机可读介质](https://www.patentguru.com/CN113360157A) 2021-09-07 applied
  - [资源计算方法、装置、电子设备及可读存储介质](https://www.patentguru.com/CN113296837B) 2025-02-28 **granted**
- Coordinate software and hardware Optimization for CNN & DNN Accelerator implemented in FPGA (2018.7-2019.10)
  - Implement CNN Operation like Conv/DeConv and DNN Operation like matmul/relu
  - Proposed a splitting HD pictures algorithm for Limited on-chip memory
  - Graph Optimization like Concat/Slice/Fusion

#### ShanDong Univ. Embedded and System Labs

- [Energy Efficient Object Detection for Edge Computing](https://github.com/xiaoyuuuuu/dac-hdc-2018-object-detection-in-Jetson-TX2)
  - [3rd place in DAC 2018 System Design Contest](http://www.cse.cuhk.edu.hk/~byu/2018-DAC-SDC/index.html)
  - Implemented half-precision calculation on GPU (Jetson TX2), with network pruning and reduced down-sampling rate

- NVM in GPGPU Memory Hierarchy
  - [Shared Last-level Cache Management for GPGPUs with Hybrid Main Memory](https://ieeexplore.ieee.org/abstract/document/7926953/) (DATE 2017, **Best Paper Award Nominations**)
  - [Shared Last-Level Cache Management and Memory Scheduling for GPGPUs with Hybrid Main Memory](https://dl.acm.org/doi/10.1145/3230643) (ACM TECS, Volume 17 Issue 4, August 2018)
- Cache Coherence Research in GPGPU
  - [基于编译器辅助的GPGPU缓存一致性研究](https://kns.cnki.net/KCMS/detail/detail.aspx?filename=1018107394.nh&dbname=CMFD201901&dbcode=cdmd) (Master Thesis 2018)
