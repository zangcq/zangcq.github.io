---
title: YOLO搭建安装过程
tags: []
id: '496'
categories:
  - - 机器学习
date: 2017-12-20 11:59:23
---

# `yolo` 搭建安装过程

## 0.Over View

`yolo`作为一个目标检测的模型,它相对突出的地方就是实时.

最新`yolo9000`这篇论文相对于`SSD`等模型也不落下风,由于我们要运行的平台是嵌入式平台,其计算资源非常有限,所以我们就需要对于实时性要求更高的模型.

前面踩得坑有 faster-rcnn,ssd,goturn等,也会有相关文章介绍.

## 1.安装过程

首先,我们来到`YOLO`官方网站

> [https://pjreddie.com/darknet/yolo/](https://pjreddie.com/darknet/yolo/)

我们按照这个网站 一步一步去做就好了,看下面

1.  相关依赖
    
    ```shell
    
    both OpenCV 3.x and OpenCV 2.4.13
    both cuDNN 5 and cuDNN 6
    CUDA >= 7.5
    ```
    
    opencv的安装 [https://zangcq.me/?p=494](https://zangcq.me/?p=494)
    
    cuda 安装 [https://zangcq.me/?p=160](https://zangcq.me/?p=160)
    
    cudnn安装 [https://zangcq.me/?p=500](https://zangcq.me/?p=500)
    

1.  首先从`github`上克隆下来,并编译
    
    ```shell
    
    git clone https://github.com/pjreddie/darknet
    cd darknet
    make
    ```
    
    编译的时候请注意,看一下`Makefile`文件
    
    ```shell
    
    GPU=0     #是否需要用GPU,当然需要了
    CUDNN=0   #是否需要用CUDNN,这是NVIDIA做的一些优化,实际上就是一些库文件,优化一些常用的矩阵操作
    OPENCV=0  #用来对图片进行操作,打开,画图等等,如果你不用的话,,在测试时就不会有直接显示图片的效果
    OPENMP=0  #CPU的多线程
    #Arch 就是GPU的架构版本 简单说一下
    ARCH= -gencode arch=compute_20,code=[sm_20,sm_21] \# Fermi 架构 常见 gtx480 gtx580
          -gencode arch=compute_30,code=sm_30 \# Kepler 架构 常见 gtx680 
          -gencode arch=compute_35,code=sm_35 \# Kepler 架构 常见 gtx780 
          -gencode arch=compute_50,code=[sm_50,compute_50] \# Maxwell 架构 常见 gtx750Ti gtx8 到9 系列 M
          -gencode arch=compute_52,code=[sm_52,compute_52]# Maxwell 架构 常见 gtx8 到9 系列
          -gencode arch=compute_61,code=[sm_61,compute_61]# Pascal 架构 常见 gtx 10系列
          -gencode arch=compute_70,code=[sm_70,compute_70]# Volta 架构 这个不常见,用作超算或者数据中心的,新出了一款2999刀的volta卡 Tesla V100,值得入手.
    
    #最后说明一下,高版本code不能在低版本的卡上跑,架构不同的其特性也有差距,所以尽量查一下你的显卡是在那个计算能力上的
    ```
    
    特别说明一下,如果在嵌入板子 Jetson TX1 或者TX2的话,也要相应修改`arch`
    
    ```shell
    
    -gencode arch=compute_53,code=[sm_53,compute_53]# Maxwell 架构 TX1
    -gencode arch=compute_62,code=[sm_62,compute_62]# Pascal 架构  TX2
    ```
    
    NVIDIA产品计算能力的链接
    
    > [https://developer.nvidia.com/cuda-gpus](https://developer.nvidia.com/cuda-gpus)
    
2.  下载 已经训练好的权值文件
    
    我们有两权值模型,`yolo`应该是32层的网络,而`tiny-yolo` 是15层,更轻量级
    
    `yolo.weights`
    
    ```shell
    
    wget https://pjreddie.com/media/files/yolo.weights
    ```
    
    `tiny-yolo-voc.weighs`
    
    ```shell
    
    wget https://pjreddie.com/media/files/tiny-yolo-voc.weights
    wget https://pjreddie.com/media/files/tiny-yolo.weights
    ```
    
3.  测试一下是否能用
    
    ```shell
    
    ./darknet detect cfg/yolo.cfg yolo.weights data/dog.jpg
    
    ./darknet detector test cfg/voc.data cfg/tiny-yolo-voc.cfg tiny-yolo-voc.weights data/dog.jpg
    ```
    
    你还可以在`data`文件夹下,找到更多的图片进行测试,这里就不赘述了.
    
4.  检测阈值的调节
    
    实际上不论 `yolo`还是`ssd`他们都是有好多候选框来检测这个目标的,我们总是去概率最大的几个来输出.
    
    我们可以用`-thresh value`,`value`来作为输出的阈值, 当`value = .5`含义就会只输出概率大于`50%`的候选框,,如果我们把阈值设置成0,那么我们会看到很多的候选框.
    
    ```shell
    
    ./darknet detect cfg/yolo.cfg yolo.weights data/dog.jpg -thresh 0
    ./darknet detect cfg/yolo.cfg yolo.weights data/dog.jpg -thresh .5
    ```
    
    大家可以自己试一下,我就不放图了.
    
5.  利用摄像头,实时检测
    
    这一步的话,我们就需要用 `opencv`来编译了,我们还需要用到一个摄像头,将它插在主机上.
    
    执行
    
    ```shell
    
    ./darknet detector demo cfg/coco.data cfg/yolo.cfg yolo.weights
    ```
    
    我们就可以看到摄像头的直接输出,还会显示当前是实时FPS,类别等等
    

## 2.训练过程

### 2.1处理`VOC`的数据集

1.  下载
    
    ```shell
    
    wget https://pjreddie.com/media/files/VOCtrainval_11-May-2012.tar
    wget https://pjreddie.com/media/files/VOCtrainval_06-Nov-2007.tar
    wget https://pjreddie.com/media/files/VOCtest_06-Nov-2007.tar
    tar xf VOCtrainval_11-May-2012.tar
    tar xf VOCtrainval_06-Nov-2007.tar
    tar xf VOCtest_06-Nov-2007.tar
    ```
    
2.  用脚本生成 Labels
    
    ```shell
    
    wget https://pjreddie.com/media/files/voc_label.py
    python voc_label.py
    ## 生成对应的 train.txt
    ```
    
3.  处理自己的数据集
    
    与处理VOC的数据集一致
    
    参考链接
    
    > [http://blog.csdn.net/sinat\_30071459/article/details/50723212](http://blog.csdn.net/sinat_30071459/article/details/50723212)
    > 
    > [http://www.cnblogs.com/qw12/p/6185126.html](http://www.cnblogs.com/qw12/p/6185126.html)
    

### 2.2 修改`darknet` 配置文件

1.  修改 `cfg/voc.data`
    
    ```shell
    
      classes= 20   #对象的类
      train  = <path-to-voc>/train.txt #voc_label.py生成的 train.txt
      valid  = <path-to-voc>2007_test.txt ##voc_label.py生成的 test.txt
      names = data/voc.names #类的名字
      backup = backup #生成权值文件的地方
    ```
    
2.  修改`cfg/tiny-yolo.cfg`
    
    这主要是`tiny-yolo`定义的一些网络结构,炼金术士们通常会对这个做一下修改.
    
    我主要简单修改一下 目标的类别 和最后一层的 filters
    
    ```shell
    
    classes = 98 
    #最后一层region
    filters=num×（classes + coords + 1）=5*(98+4+1)=515
    ```
    
    就举个例子说明一下.
    
3.  下载预训练模型
    
    ```shell
    
    wget https://pjreddie.com/media/files/darknet19_448.conv.23
    ```
    
4.  生成自己的预训练权值
    
    ```shell
    
    ./darknet partial cfg/darknet19_448.cfg darknet19_448.weights darknet19_448.conv.23 23
    ```
    

### 2.3 训练模型

1.  训练`voc`
    
    ```shell
    
    ./darknet detector train cfg/voc.data cfg/yolo-voc.cfg darknet19_448.conv.23
    ```
    
    如果想训练其他的模型,我们修改这两个 配置文件就行了`cfg/voc.data` `cfg/yolo-voc.cfg`
    
2.  训练`coco`
    
    ```shell
    
    ./darknet detector train cfg/coco.data cfg/yolo.cfg darknet19_448.conv.23
    ```
    
3.  多个`gpu`训练(同一机器),似乎不能分布式训练
    
    ```shell
    
    ./darknet detector train cfg/coco.data cfg/yolo.cfg darknet19_448.conv.23 -gpus 0,1,2,3
    ```
    

### 3.测试

`TX2`作为测试平台,编译安装过程是一样的,所以不在多说了.

我们同时在 带有`1080Ti`的服务器和`Jetson TX2`上搭建环境,服务器用作训练,而嵌入式板卡`TX2`作为测试,效果测试会在后续优化的文章中说明

## Reference

> [https://pjreddie.com/darknet/yolo/](https://pjreddie.com/darknet/yolo/)
> 
> [http://blog.csdn.net/qq\_14845119/article/details/53589282#t3](http://blog.csdn.net/qq_14845119/article/details/53589282#t3)
> 
> [http://www.yuthon.com/2016/11/12/Train-YOLO-on-our-own-dataset/](http://www.yuthon.com/2016/11/12/Train-YOLO-on-our-own-dataset/)
> 
> [http://blog.csdn.net/u011475210/article/details/78090344](http://blog.csdn.net/u011475210/article/details/78090344)
> 
> [https://github.com/AlexeyAB/yolo2\_light](https://github.com/AlexeyAB/yolo2_light)