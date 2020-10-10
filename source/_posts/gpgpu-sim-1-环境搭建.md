---
title: GPGPU-Sim 1 环境搭建
tags: []
id: '916'
categories:
  - - gpu-computing
    - GPGPU-Sim Notes
date: 2018-05-09 22:46:31
---

# GPGPU-Sim 1 环境搭建

前一篇文章我们简要介绍了`GPGPU-Sim`概况，那么本文主要介绍`GPGPU-Sim`的环境搭建。

`GPGPU-Sim`环境搭建主要有三种方式：

*   直接安装
*   下载官方虚拟机
*   前两项的折衷

`GPGPU-Sim`用CPU单线程来模拟GPU的多线程，那么必然会降低运行速度，直接安装的效果相对是最快的，而使用虚拟机则是最慢的选择，那我们分别来介绍这三种方法。

## 直接安装

给出下列几篇参考，但不建议，因为坑太多，可以了解一下。

> [http://linux-article-collections.blogspot.sg/2015/01/gpgpu-sim-installation.html](http://linux-article-collections.blogspot.sg/2015/01/gpgpu-sim-installation.html)
> 
> [https://blog.csdn.net/litdaguang/article/details/44424085](https://blog.csdn.net/litdaguang/article/details/44424085)

## 官方虚拟机

官网提供的是`vbox`的镜像，操作系统`ubuntu 12.04`，直接从官网下载即可。

> [http://ece.ubc.ca/](http://ece.ubc.ca/)~taylerh/files/gpgpu-sim/gpgpu-sim.vm.tar.gz

直接解压导入virtual box 即可。

## 折中方法

有`litdaguang`提出，经过稍加修改。

> [http://blog.csdn.net/litdaguang/article/details/50002325](http://blog.csdn.net/litdaguang/article/details/50002325)

*   **从虚拟机中获得所需要的文件**

1.  `/home/gpgpu-sim/cuda/toolkit/4.2/cuda/bin`
    
    `gpgpu-sim`的`cuda toolkit 4.2`的环境，其中包含`nvcc`等等
    
2.  `/home/gpgpu-sim/gpgpu-sim_distribution/lib/gcc-4.6.4/cuda-4020/release`
    
    `gpgpu-sim`的模拟环境，生成的`.so`文件
    

*   **建立本机工作文件夹**

1.  新建一个文件夹`sim`
    
    ```sh
    
    mkdir sim
    ```
    
2.  将`bin`和`release`两个文件夹拷贝到新建的文件夹
    
    ```sh
    
    cp -r bin/ sim/
    cp -r release sim/
    ```
    

*   **设置`gpgpu-sim`环境变量**
    
    此方法与cuda环境变量设置相同
    
    例如
    
    ```sh
    
    #将目录替换成自己的即可
    export PATH=/home/zagncq/Desktop/sim/bin:$PATH
    export LD_LIBRARY_PATH=/home/zagncq/Desktop/sim/release
    ```
    
    建议设置临时环境变量，即在本窗口下有效，而不是对本机有效。这样不会对本机其他环境造成影响。
    
*   **判断环境是否生效**
    
    ```sh
    
    zagncq@zagncq-OptiPlex-7010:~/Desktop/gpgpu-sim$ nvcc --version
    
    nvcc: NVIDIA (R) Cuda compiler driver
    Copyright (c) 2005-2012 NVIDIA Corporation
    Built on Thu_Apr__5_00:24:31_PDT_2012
    Cuda compilation tools, release 4.2, V0.2.1221
    ```
    
    当出现 `cuda` 版本4.2时，表示环境配置有效。那么我们在本窗口（`terminal`）下即可模拟`gpgpu-sim`的环境。
    
*   将`GTX480`配置文件和需要运行的可执行程序 复制到`sim`文件夹下，即可得到相应的性能结果
    
    1.配置文件
    
    gpgpusim.config
    
    gpuwattch\_gtx480.xml config\_fermi\_islip.icnt
    
    2.运行`benchmark`
    
    $$# run benchmark ./LPS$$