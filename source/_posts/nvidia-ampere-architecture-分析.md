---
title: NVIDIA Ampere Architecture 分析
tags: []
id: '1297'
categories:
  - - GPGPU
comments: false
date: 2020-05-17 11:39:59
---

官方博客

[https://devblogs.nvidia.com/nvidia-ampere-architecture-in-depth/](https://devblogs.nvidia.com/nvidia-ampere-architecture-in-depth/)

知乎讨论

[https://www.zhihu.com/question/394863138](https://www.zhihu.com/question/394863138)

个人观点

知乎回答

1.  7nm工艺下 108/128 的良品率还是挺高的
2.  单SM，FP32/INT32/FP64 没有变化，单个Tensor Core 从 4\*4\*4 变为 4\*8\*8 的计算核心，并且增加了硬件稀疏化的功能，这个确实令人佩服。L1 cache又加了几十KB。
3.  单GPU， MIG这个功能总算盼到了，云厂商的虚拟化工作应该更容易做了，L2 Cache扩到 40M 来服务于 108个SM
4.  多GPU互联，NVLINK 3.0，不太懂互联技术，感觉带宽提高了
5.  CPU-GPU互联，PCIE 4.0 的升级; 确实很多情况都是IO的瓶颈
6.  6显存HBM2 接口没变化，容量增大到40G
7.  其实，首先想到的是，互联网自研芯片，可能只是为了有跟nv议价的能力，但是像A100这种全能选手，平头哥含光800 好像不是一个公斤级的了。

一些有趣的观点

夏晶晶，很早关注的，应该是计算所的老哥。，海思的大佬，升腾、鲲鹏的芯片架构师，牛笔！

[https://www.linkedin.com/in/%E6%99%B6-%E5%A4%8F-49a9a5123/](https://www.linkedin.com/in/%E6%99%B6-%E5%A4%8F-49a9a5123/)

*   首先肯定了 A100 是 AI 炼丹神器
*   其次讲了 NV 在 HPC (高性能计算领域) 的出局，（这个本人不了解）
*   最后讲了 如 Intel Amd 华为的等公司将在HPC领域的崛起

其实我们要从NV架构的历史看待这个问题的话，就容易理解这次新的升级了。

*   7nm 工艺的红利，
    *   更高的集成度 540 亿晶体管，826 mm2 ！
*   面向热门应用的芯片设计，由近及远
    *   Ampere，Turing，Volta ：加持了Tenor Core 一个专门为做矩阵乘的ASIC，很明显就是为了Deep Learning 类的应用做的
    *   Pascal，Maxwell，Kepler，Fermi ： 主要以CUDA Core 用于 FP32/FP64, 主要解决的问题是 通用计算，也就是以前 CPU 干的活
    *   Tesla 之前的架构， 其实并没有进入 计算领域，主要用作图像的显示，也就通俗讲的消费级显卡。处理pixel
*   系统级别的全面优化
    *   从GPU之间的互联，Nvlink ，nvswitch
    *   与CPU的互联技术，PCIE
    *   显存的接口，协议，增加带宽。

显而易见，NV明显吃到了深度学习的这波红利，并且押宝自动驾驶这个方向，所以夏总说，放弃了HPC也是正常的现象。因为体系结构，除非有突破性的变革，那就只能一点一点挤牙膏了，让单位面积的晶体管，发挥出他的最大能效。