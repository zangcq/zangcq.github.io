---
title: 关于NV端侧SOC算力的计算公式
tags: []
id: '1028'
categories:
  - - GPGPU
  - - 日常扯淡
comments: false
date: 2019-11-16 11:57:12
---

#### Reference

1.  [https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-tx2/](https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-tx2/)
2.  [https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-nano/](https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-nano/)
3.  [https://devblogs.nvidia.com/nvidia-jetson-agx-xavier-32-teraops-ai-robotics/](https://devblogs.nvidia.com/nvidia-jetson-agx-xavier-32-teraops-ai-robotics/)
4.  [https://developer.nvidia.com/embedded/jetson-xavier-nx](https://developer.nvidia.com/embedded/jetson-xavier-nx)  
    
5.  [https://images.nvidia.com/content/volta-architecture/pdf/volta-architecture-whitepaper.pdf](https://images.nvidia.com/content/volta-architecture/pdf/volta-architecture-whitepaper.pdf)  
    
6.  [https://docs.nvidia.com/cuda/cuda-c-programming-guide/index.html#arithmetic-instruction](https://docs.nvidia.com/cuda/cuda-c-programming-guide/index.html#arithmetic-instructions)

#### Overview

最近NVIDIA又出了一款边缘计算的SOC（systom on chip），之前用过NV最初的SOC，因此就临时起意，整理一个这个表出来，当然TK1和TX1已经out of date了，因此就不再进行比较了。

##### Table of NVIDIA Edge SoC for AI

SOC

TX2

Nano

Xavier

Xavier NX

Arch

Pascal

Pascal

Volta

Volta

SMs

2

1

6/8

6

SPs

256

128

384/512

384

Tensor Core

\*

\*

48/64

48

FP16 Compute (FLOPS)

1.3T

0.5T

5.5+4.1 / 11+5 T

INT8 Compute OPS

11.1+8.2 / 22+10 T

14T at 10W 21T at 15W

Memory（GB）

4/8

4

8/16

16

Price ($)

399/479

99

699

399

在读书期间对NV GPU的体系结构有一些理解，当然很浅；当然有两个架构令人印象深刻，第一个Fermi架构，他开启NV进入通用计算的行列，另一个便是Volta架构，他在首先在GPU上集成AISC 的Tensor Core，专门做matrix multiply（矩阵乘），因此算力才有成倍的提升。

##### FLOPS 和OPS

我们看到NV或者其他芯片公司常常说芯片提供了多少算力，从几T到几百T不等，一会儿时FLOPS，一会儿是OPS，令我们常人看了费解，只是看着数字说句NB。实际上呢，也不难理解，那么我们就来详细算一下这些TFLOPS是怎么来的。

我们知道GPU常用的数据类型实际上float，我们常称之为 FP32，那么FP就float的缩写，而FLOPS实际上就是

float operation per second，每秒浮点数运算数，来作为处理器的性能。如果一个处理器每秒钟只能计算一次浮点数的加法，那么他的性能就是1FLOPS；

OPS常见的就是INT8的类型，就是8位的整数，-128到127的范围。我们知道数据位数越长，那么对应每次运算时间就会越长，我们可以看到FP16（16位浮点数）常常是INT8类型的二分之一算力。而fp32就是INT8类型的四分之一了。所以为了发布会效果，我们常常看到皮衣黄教主用INT8数据的算力来忽悠大家。当然，也是很高的了。

根据笔者的经验，在精度要求不是太高的场景，比如目标检测，图像识别中，INT8是可以满足需求的，而想搜索推荐的场景，常用的是FP16的数据类型，INT8数据类型的算法精度还不可用。

##### FLOPS计算公式

###### 1\. cuda core的计算方式

我们首先来看传统的cuda core的计算方式

我们以TX2为例；

http://www.zangcq.com/2017/12/18/jetson-tx2-%e6%80%a7%e8%83%bd%e6%a8%a1%e5%bc%8f%e5%b7%a5%e5%85%b7nvpmodel/

我在一篇工具文章中记录了一下TX2的主频为1.3GHz；

TX2 共有2 个Pascal 的SMs；每个SM呢又有128个小SP，

每个SP在一个时钟周期内可以做一次FMA（fused multiply add）乘法和加法，那么也就是2次FP32类型数据FLOPS，那么总共算力就可以得到：

总算力 = 主频 x SMs数 x 每个SM可以计算的最高乘加 x 2 （fma）

1.3GHz x 2 （SMs）x 128 x 2 FLOPS = 665.6G FLOPS

![](https://img-blog.csdn.net/20180417155049741?watermark/2/text/aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L2Rhcms1NjY5/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70)

根据之前的残留的表上可以看到，

TX2对应计算能力6.2时，，fp16的算力，即为

1.3GHz(Max Freq) x 2 （SMs）x 256 x 2 FLOPS = 1.3T FLOPS了，证明还是可以算对的。

同样如果想得到 INT8类型的数据的话，也就是FP16两倍的算力罢了。

那么同样的我们看一下Xavier NX 的CUDA Core的算力，

如 reference 4 中Tech Specs所示，它的主频是800Mhz，384个CUDA Core，通过我最上边的表可以知道，其实NX的CUDA Core算力大概跟 Xavier 8G内存版本相当，在 5.5T FP16 左右，我们来验证一下。

800 Mhz x 6 SMs x 128 x 2 =

###### 2\. tensor core

tensor core第一次引入是在volta架构，那么我们从白皮书\[5\]可以看到对应的计算方式。

在volta架构中，每个SM中有8个Tensor Core，每两个tensor core在一个处理单元里。

每个Tensor Core 每个clock可以处理 64个FP16浮点的乘加，那么这就比每个CUDA core提升了64倍计算效率了。

那么我们同样用算力公式来计算一下。

**Xavier 的算力 512-core NVIDIA Volta @ 1377MHz with 64 TensorCores**

主频 x SMs x Tensor Core num Per SM x 64 x 2 FLOPS =

SMs x Tensor Core num Per SM 简化为 total tensor core num

1377Mhz x 64 Tensor Cores x 64 FP16 x 2 FLOPS = 10.758 TFLOPS

我们把公式整理一下

**总算力 = CUDA Core 算力 + TENSOR Core 算力**

**CUDA Core 算力 = 主频 x SMs数 x 每个SM可以计算的最高乘加 x 2 FLOPS（fma）**

**TENSOR Core 算力 = 主频 x SMs数 x Tensor Core num Per SM x 64 x 2 FLOPS （fma）**

**Xavier 的算力 512-core NVIDIA Volta @ 1377MHz with 64 TensorCores**

512-core 为8 个64CUDA core SM；

128为 每个CUDA Core FP16的计算fma最大计算数；

代入公式可以得到

1.  1377 MHz x 8 SMs x 128 FP16 x 2 FLOPS = 2.689 TFLOS
2.  1377 MHz x 8 x 8 x 64 x 2 FLOPS = 10.758 TFLOPS

那么total 算力为 13.4 FLOPS（FP16）；那么跟上表中 总共INT8（在FP16基础上乘2）算力32OPS是有出入的。

[https://devblogs.nvidia.com/nvidia-jetson-agx-xavier-32-teraops-ai-robotics/](https://devblogs.nvidia.com/nvidia-jetson-agx-xavier-32-teraops-ai-robotics/)

update

Xavier实际上还集成2 x DeepLearning Accelerator，提供了5TOPS的算力，这样与 13.4x2 = 26.8 + 5 与声称的32TOPS就可以对齐了。

##### 小结

尽管经过计算后总的算力是有出入的，但是与其他芯片厂家提供的端上的芯片来说还是相对较高的，算力从云数据中心的战场已经迁移到了端侧，虽然应用场景还在安防等领域，我想在很快的一段时间内，还是会出现一场厮杀的。芯片行业是赢者通吃的局面，华为是一个搅局者，当然国产化的需求在某些方面是政府的需要，但是真正的市场，才是行业的未来。

本文只是介绍了nv的端侧SOC算力的计算方法，并没有对其他厂商进行比较，当然如高通，英特尔，华为，habana，xilinx等等都会加入这个战局，但是论云与端侧的生态，CUDA已经吊打所有人了。