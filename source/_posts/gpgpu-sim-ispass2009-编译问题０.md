---
title: GPGPU-Sim ispass2009 编译问题０
tags:
  - GPGPU-Sim
  - GPU
  - Shell
id: '278'
categories:
  - - gpu-computing
    - GPGPU-Sim Notes
date: 2017-08-09 09:41:44
---

# GPGPU-Sim ispass2009 编译问题０

最早接触GPU-SIM时的几个问题．**thanks the reply for wdw**

## Question

1.  AES
    
    在编译AES的时候，一直出现这个错误`“fatal error: boost/filesystem/operations.hpp: No such file or directory”` 是不是缺少了什么依赖呢 `Google`了一下 安装`了libboost-all-dev,`但是还是没有用，
    
2.  DG
    
    编译时老出现“`fatal error: mpi.h: No such file or directory`” 但是我在系统上也安装了`libcr-dev mpich2`的依赖了，`include`的时候是<>还是找不到对应`mpi.h`
    
3.  WP
    
    WP已经被我编译完成了，但是根据`readme`运行的时候老是出现错误，程序不能找到输入文件，，但是文件确实在`/data`中
    

## response

关于你的问题回答如下：

1.  我的`AES`已经编译成功，你需要安装`boost`的库才可以，正确的包含头文件和库文件，就没有问题
    
2.  `DG`你缺少的是mpi， 他需要一个库文件，就是他的文件夹下面的那个`3rdparty`， 你在编译`DG`之前首先需要编译成功这个库，他生成两个.a的文件，后续的DG的编译需要调用。我的理解是这个第三方库的编译需要`mpi`，同样的是安装`mpi`之后使用`mipcc`编译。但是我的第三方库编译成功之后，正常的文件的编译遇到了很多的问题。
    
3.  我刚才由看了一下我的`wp`， 已经编译成功并运行起来了，你需要输入命令：
    
    `sh README.GPGPU-Sim`
    
    这个文件其实是运行的脚本程序，`readme`里面的东西很多确实是不存在的
    

## WP编译过程

ispass2009中一共有12个benchmarks，直接编译能用的有9个。 WP是（weather forecast）天气预测的意思。 这是第十二个，我想用一下，因此单独编译。 在WP文件夹中也是有单独的makefile 的。

**0\. 编译一下**

```shell

cd ispassbenchmark/WP
make
```

出现如下结果

![img](http://img.blog.csdn.net/20160601211000737?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQv/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/Center)

1.  `gfortran :not found`
    
    缺少了一个编译器，`gFortran` 类似`gcc/g++`的编译器。
    
    这个好办，装上就行了,
    
    $$sudo apt-get install gfortran$$
    
    下面这个链接就是怎装gfortran的，参考一下
    
    > [http://askubuntu.com/questions/358907/how-do-i-install-gfortran](http://askubuntu.com/questions/358907/how-do-i-install-gfortran)
    
2.  `在/usr/bin/ld 找不到 -lcutil_x86_64`
    
    继续编译后出现错误
    
    ![](http://img.blog.csdn.net/20160601212125841?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQv/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)
    
    在/usr/bin/ld 找不到 -lcutil\_x86\_64 那么直接的方法，就是找到它
    
    ```shell
    
    find -name “libcutil_x86_64*”
    ```
    
    发现在 `/home/gpgpu-sim/cuda/sdk/4.2/CUDALibraries/common/lib`
    
    走了一些弯路
    
    > [http://blog.sina.com.cn/s/blog\_4156950c0100sfzz.html](http://blog.sina.com.cn/s/blog_4156950c0100sfzz.html)
    > 
    > [https://devtalk.nvidia.com/default/topic/513646/ld-cannot-find-lcutil-have-make-cuda-sdk-/](https://devtalk.nvidia.com/default/topic/513646/ld-cannot-find-lcutil-have-make-cuda-sdk-/)
    
    上边两个链接对着个来说也没啥用，原来是`cuda sdk` 的路径不对，在`makefile` 里加上绝对路径就好了
    
    如下图
    
    ![img](http://img.blog.csdn.net/20160601220118321?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQv/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)
    
3.  `wsm.f.cu.cpp:no such file or directory`
    
    ![](http://img.blog.csdn.net/20160601220231963?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQv/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)
    
    没有这文件，好吧，，看了一眼makefile，又看了WP的目录，确实不匹配，改makefile。 在编译的时候，没有\*\*\*.cpp,目录里是。cpp.ii
    
    改一下
    
    ![img](http://img.blog.csdn.net/20160601220556844?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQv/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)
    
4.  错误解决完了，编译成功！
    
    ![img](http://img.blog.csdn.net/20160601221035802?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQv/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)
    
    生成可执行文件．
    
5.  运行
    
    ```shell
    
    sh README.GPGPU-Sim
    or
    echo "10 ./data/" ./bin/release/WP
    ```
    
    **注意**：
    
    出现了点问题，gpgpusim.config文件和gpuwattch\_gtx480.xml ，，还有这个config\_fermi\_islip.icnt没找到。。 从GTX480 RUNDIR 中copy到WP目录下过去就行。
    
6.  done