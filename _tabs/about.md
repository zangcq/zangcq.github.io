---
icon: fas fa-info-circle
order: 5
lang: zh-CN
lang-exclusive: ["zh-CN"]
page_id: about
---
目前在字节跳动基础架构部门担任系统软件工程师，专注于 Java 工作负载的优化与问题排查。

加入字节之前，我在[阿里云基础架构](https://www.alibabacloud.com/)工作了两年。硕士毕业于[山东大学](https://www.sdu.edu.cn/)计算机体系结构专业，师从[鞠雷](https://faculty.sdu.edu.cn/julei)老师。

### 项目经历

#### 字节跳动基础架构 | 编译器与库组（2020.7 ~ 至今）

- 字节跳动OpenJDK技术负责人
  - 自研构建 OpenJDK 二进制，提供基础 Docker 镜像与数据中心 JDK 部署
  - 主导公司大数据服务JDK8到JDK17的版本升级，落地规模超过千万核。
  - 深入理解 GC、JIT、运行时系统，擅长内存泄漏与 Coredump 问题排查。
- 深入分析数据中心工作负载，制定优化方案并落地。
  - 设计并实现G1弹性堆内存的方案，业务增强垂直扩缩容能力。
  - 设计并实现应用透明大页到CodeCache和LibJVM方案，提升iTLBCache命中率。
  - 深度参与 x86、ARM、RISC-V架构服务器引入及性能调优。

#### 阿里巴巴基础架构 | 异构计算编译器组（2018.7 ~ 2020.7）

- 蚂蚁区块链平台 Wasm AOT 编译器框架（2019.9 ~ 2020.6）
  - 将 Wasm 字节码转换为 LLVM IR，并为 RISC-V ISA 添加 T-Head CSKY 扩展
  - [一种程序编译方法、设备以及计算机可读介质](https://www.patentguru.com/CN113360157A) 2021-09-07 已申请
  - [资源计算方法、装置、电子设备及可读存储介质](https://www.patentguru.com/CN113296837B) 2025-02-28 **已授权**
- FPGA CNN & DNN 加速器软硬件协同优化（2018.7 ~ 2019.10）
  - 实现 Conv/DeConv 等 CNN 算子与 matmul/relu 等 DNN 算子
  - 针对片上存储受限场景提出高清图片切分算法
  - 进行 Concat/Slice/Fusion 等计算图优化

#### 山东大学嵌入式与系统实验室

- [面向边缘计算的低功耗目标检测](https://github.com/xiaoyuuuuu/dac-hdc-2018-object-detection-in-Jetson-TX2)
  - 获得 [DAC 2018 System Design Contest 第三名](http://www.cse.cuhk.edu.hk/~byu/2018-DAC-SDC/index.html)
  - 在 GPU（Jetson TX2）上实现半精度计算，网络剪枝与降低下采样率

- GPGPU 存储层次中的 NVM 研究
  - [Shared Last-level Cache Management for GPGPUs with Hybrid Main Memory](https://ieeexplore.ieee.org/abstract/document/7926953/)（DATE 2017，**最佳论文提名**）
  - [Shared Last-Level Cache Management and Memory Scheduling for GPGPUs with Hybrid Main Memory](https://dl.acm.org/doi/10.1145/3230643)（ACM TECS, Volume 17 Issue 4, August 2018）
- GPGPU 缓存一致性研究
  - [基于编译器辅助的GPGPU缓存一致性研究](https://kns.cnki.net/KCMS/detail/detail.aspx?filename=1018107394.nh&dbname=CMFD201901&dbcode=cdmd)（硕士学位论文 2018）
