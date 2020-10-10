---
title: Jetson TX2 安装 JetPack 3.0 小记 与 申请教育版链接
tags:
  - CUDA
  - GPU
  - Shell
id: '129'
categories:
  - - gpu-computing
    - Jetson TX1-2
date: 2017-06-26 09:29:33
---

## 前言

本文主要参考YouTube视频，《JetPack 3.0 - NVIDIA Jetson TX2》

视频链接如下：

> [https://www.youtube.com/watch?v=D7lkth34rgM](https://www.youtube.com/watch?v=D7lkth34rgM)

国外主要研究NVIDIA JETSON系列的网站[JetsonHacks](http://www.jetsonhacks.com/)

> Install JetPack 3.0 on a NVIDIA Development Kit. JetPack 3.0 can flash the Jetson TK1, TX1 and TX2. Please Like, Share and Subscribe! Full article on JetsonHacks: [http://wp.me/p7ZgI9-Ly](http://wp.me/p7ZgI9-Ly)

鉴于国内网络情况，放一个百度云连接吧

> 链接: [https://pan.baidu.com/s/1pLjYjTx](https://pan.baidu.com/s/1pLjYjTx) 密码: fagi

英伟达 install guide

> [http://docs.nvidia.com/jetpack-l4t/index.html#developertools/mobile/jetpack/l4t/3.0/jetpack\_l4t\_install.html](http://docs.nvidia.com/jetpack-l4t/index.html#developertools/mobile/jetpack/l4t/3.0/jetpack_l4t_install.htm)

## 广告？福利

给英伟达做一个广告吧，对学生党或者来说是一个福利。 这款嵌入式板卡电脑是对教育用户是优惠的，之前实验室的TK1，TX1都是淘宝代购来，价格比原价还贵，还是有些坑。原来英伟达只面向欧美学校，现在终于开始了对中国大学的优惠。

放一个教育专属的申请连接

> TX1 [http://www.nvidia.cn/object/edu-discount-cn.html](http://www.nvidia.cn/object/edu-discount-cn.html) TX2 [http://www.nvidia.cn/object/jetsontx2-edu-discount-cn.html](http://www.nvidia.cn/object/jetsontx2-edu-discount-cn.html)

还是郑重声明，做人以诚信为本，切莫贪婪！

## 流程简介

说一下总体流程，其实我在前一篇关于TK1 刷机的文章里提过，刷机对嵌入式板卡电脑来说就是装系统，而JetPack3.0 呢，实际就是通过PC对其搭个cuda或者tensorRF的环境而已。

1.  一台 装有 Ubuntu 16.04 64bit PC 机 我们当做 host 端
2.  jetson tx2 作为device端
3.  将JetPack 3.0 安装至 host端，并且将各种安装包，下载下来。
4.  将device 与 host 通过 usb 数据线进行连接，并进入recovery 模式
5.  通过引导程序，进行一步步操作。

JetPack 下载链接

> [https://developer.nvidia.com/embedded/jetpack](https://developer.nvidia.com/embedded/jetpack)

## 坑

其实我并没有成功的安装JetPack，仅仅将cuda 装上了。 这个bug就是出现在要进行网络连接时，我在tx2上的ip 一直未获取到。 其实他的原理也是很简单，通过host端的eth0 来给tx2一个局域网的网址，然后通过ssh，进行连接，然后安装。

尝试了几次之后，（没重启，说不定重启可以解决问题），打开到JetPackdownload 文件夹，一下看到了 cuda 的deb 文件，好吧，直接拷贝过去，安装完成了。

TX2 确实比TX1 提升了不少，首先arm处理器（不是很懂），然后架构pascal，RAM跟ROM 都加了一倍。

虽然未来是FPGA的，但是现在玩玩也不错。