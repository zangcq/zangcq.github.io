---
title: cudnn Installation in Linux
tags: []
id: '500'
categories:
  - - 机器学习
date: 2017-12-20 15:50:48
---

# `cudnn` Installation in Linux

安装教程相对简单,实际原理就是将 `cudnn`的库加入 `cuda` 的 `include` 和 `lib` 文件夹中

## 0.前提

1.  此方法适用于Linux 系统,常见的 `Ubuntu` ,`Debian` 等等
2.  首先你的系统已经成功安装好 `CUDA toolkit`
3.  从官方网站上下载 `cudnn` 的压缩包(很多版本,下载你需要的),需要登录账户

## 1\. `Ubuntu` 下安装

1.  进入存在 cudnn\*\*.tgz 的文件夹
    
2.  解压
    
    ```shell
    
    $ tar -xzvf cudnn-9.0-linux-x64-v7.tgz
    ```
    
3.  将解压过的文件,复制到你`cuda`的安装目录即可
    
    ```shell
    
    $ sudo cp cuda/include/cudnn.h /usr/local/cuda/include
    $ sudo cp cuda/lib64/libcudnn* /usr/local/cuda/lib64
    $ sudo chmod a+r /usr/local/cuda/include/cudnn.h /usr/local/cuda/lib64/libcudnn*
    ```
    

## 2\. `Debian` 下安装

`Debian`下的安装方法跟简单,直接安装打包好的`.deb`就可以了.

1.  进入`debian`版本`cudnn`的文件夹下
    
2.  安装运行时的库
    
    ```shell
    
    sudo dpkg -i libcudnn7_7.0.3.11-1+cuda9.0_amd64.deb
    ```
    
3.  安装开发者的库
    
    ```shell
    
    sudo dpkg -i libcudnn7-dev_7.0.3.11-1+cuda9.0_amd64.deb
    ```
    
4.  安装 例程和用户指南
    
    ```shell
    
    sudo dpkg -i libcudnn7-doc_7.0.3.11-1+cuda9.0_amd64.deb
    ```
    

## 3.测试一下是否安装成功

运行一个小Demo即可.

如果安装了 例程和用户指南 这个包的话,我们可以找到位于 `/usr/src/cudnn_samples_v7`的`mnistCUDNN`这个小例子.

1.  拷贝到 你的home/yourdir 任意文件夹下
    
    ```shell
    
    $cp -r /usr/src/cudnn_samples_v7/ $HOME
    ```
    
2.  进入 `mnistCUDNN`
    
    ```sh
    
    $ cd $HOME/cudnn_samples_v7/mnistCUDNN
    ```
    
3.  编译
    
    ```shell
    
    $make clean && make
    ```
    
4.  运行
    
    ```sh
    
    $ ./mnistCUDNN
    ```
    
5.  如果安装成功了,你会看到这样结果
    
    ```shell
    
    Test passed!
    ```
    

其实还可以`cmake` 一下你的`caffe/build`,也能很快测试是否安装成功

## Reference

> [https://developer.nvidia.com/compute/machine-learning/cudnn/secure/v7.0.5/prod/Doc/cuDNN-Installation-Guide](https://developer.nvidia.com/compute/machine-learning/cudnn/secure/v7.0.5/prod/Doc/cuDNN-Installation-Guide)