---
title: fast rcnn 环境配置
tags:
  - Deep learning
  - Faster rcnn
id: '135'
categories:
  - - DAC-SDC
date: 2017-12-22 18:29:11
---

## 前言

fast rcnn是Ross B. Girshick对RCNN的一个优化,性能上有了显著提升,然而在现在看来这个模型已经相对过时,在性能较低的设备上难以做到实时.但github上的fast-rcnn项目中包含大量工具脚本,是一个caffe入门的优秀选择,在这里简单介绍一下环境的搭建以及版本问题的解决.

## 环境介绍

*   x86\_64,arm均尝试过
*   ubuntu 16.04 LTS

## 项目下载:

*   git clone _\--recursive_ [https://github.com/rbgirshick/py-fast-rcnn.git](https://github.com/rbgirshick/py-fast-rcnn.git)
    
*   安装好caffe需要的所有环境
    
    *   cuda
    *   atlas/openBlas
    *   boost-dev
    *   lmdb
    *   leveldb
    *   protobuf,glog,gflags,hdf5 等等,如果装不全,编译过程中会有相关错误,及时安装即可
*   在这里选择Python接口,按照说明把所有的依赖项走一遍就可以了 `for req in $(cat requirements.txt); do pip install $req; done`
    
    *   然而这里的一个额外问题是fast-rcnn需要其他的库,如果缺少这些库,在运行时会报错,并且会推荐你安装这些库(形如python-xxx),这时apt install它们就可以了,大概有这些
    
    *   python-opencv python-yaml python-gtk(??印象中有，错误由plt.show()调用报出): apt install
    *   cython easydict: pip\[2(可选)\] install

## 编译

*   设置Makefile.config,这里把我使用的贴过来:

```
## Refer to http://caffe.berkeleyvision.org/installation.html
# Contributions simplifying and improving our build system are welcome!

# cuDNN acceleration switch (uncomment to build with cuDNN).
#USE_CUDNN := 1

# CPU-only switch (uncomment to build without GPU support).
CPU_ONLY := 1

# uncomment to disable IO dependencies and corresponding data layers
# USE_OPENCV := 0
# USE_LEVELDB := 0
# USE_LMDB := 0

# uncomment to allow MDB_NOLOCK when reading LMDB files (only if necessary)
#You should not set this flag if you will be reading LMDBs with any
#possibility of simultaneous read and write
# ALLOW_LMDB_NOLOCK := 1

# Uncomment if you're using OpenCV 3
# OPENCV_VERSION := 3

# To customize your choice of compiler, uncomment and set the following.
# N.B. the default for Linux is g++ and the default for OSX is clang++
# CUSTOM_CXX := g++

# CUDA directory contains bin/ and lib/ directories that we need.
CUDA_DIR := /usr/local/cuda
# On Ubuntu 14.04, if cuda tools are installed via
# "sudo apt-get install nvidia-cuda-toolkit" then use this instead:
# CUDA_DIR := /usr

# CUDA architecture setting: going with all of them.
# For CUDA < 6.0, comment the *_50 lines for compatibility.
CUDA_ARCH := -gencode arch=compute_20,code=sm_20 \
-gencode arch=compute_20,code=sm_21 \
-gencode arch=compute_30,code=sm_30 \
-gencode arch=compute_35,code=sm_35 \
-gencode arch=compute_50,code=sm_50 \
-gencode arch=compute_50,code=compute_50

# BLAS choice:
# atlas for ATLAS (default)
# mkl for MKL
# open for OpenBlas
BLAS := atlas
# Custom (MKL/ATLAS/OpenBLAS) include and lib directories.
# Leave commented to accept the defaults for your choice of BLAS
# (which should work)!
# BLAS_INCLUDE := /path/to/your/blas
# BLAS_LIB := /path/to/your/blas

# Homebrew puts openblas in a directory that is not on the standard search path
# BLAS_INCLUDE := $(shell brew --prefix openblas)/include
# BLAS_LIB := $(shell brew --prefix openblas)/lib

# This is required only if you will compile the matlab interface.
# MATLAB directory should contain the mex binary in /bin.
# MATLAB_DIR := /usr/local
# MATLAB_DIR := /Applications/MATLAB_R2012b.app

# NOTE: this is required only if you will compile the python interface.
# We need to be able to find Python.h and numpy/arrayobject.h.
PYTHON_INCLUDE := /usr/include/python2.7 \
/usr/lib/python2.7/dist-packages/numpy/core/include
# Anaconda Python distribution is quite popular. Include path:
# Verify anaconda location, sometimes it's in root.
# ANACONDA_HOME := $(HOME)/anaconda
# PYTHON_INCLUDE := $(ANACONDA_HOME)/include \
# $(ANACONDA_HOME)/include/python2.7 \
# $(ANACONDA_HOME)/lib/python2.7/site-packages/numpy/core/include \

# Uncomment to use Python 3 (default is Python 2)
# PYTHON_LIBRARIES := boost_python3 python3.5m
# PYTHON_INCLUDE := /usr/include/python3.5m \
#                 /usr/lib/python3.5/dist-packages/numpy/core/include

# We need to be able to find libpythonX.X.so or .dylib.
PYTHON_LIB := /usr/lib
# PYTHON_LIB := $(ANACONDA_HOME)/lib

# Homebrew installs numpy in a non standard path (keg only)
# PYTHON_INCLUDE += $(dir $(shell python -c 'import numpy.core; print(numpy.core.__file__)'))/include
# PYTHON_LIB += $(shell brew --prefix numpy)/lib

# Uncomment to support layers written in Python (will link against Python libs)
WITH_PYTHON_LAYER := 1

# Whatever else you find you need goes here.
INCLUDE_DIRS := $(PYTHON_INCLUDE) /usr/local/include /usr/include/hdf5/serial
LIBRARY_DIRS := $(PYTHON_LIB) /usr/local/lib /usr/lib /usr/lib/x86_64-linux-gnu /usr/lib /usr/lib/x86_64-linux-gnu/hdf5/serial

# If Homebrew is installed at a non standard location (for example your home directory) and you use it for general dependencies
# INCLUDE_DIRS += $(shell brew --prefix)/include
# LIBRARY_DIRS += $(shell brew --prefix)/lib

# Uncomment to use `pkg-config` to specify OpenCV library paths.
# (Usually not necessary -- OpenCV libraries are normally installed in one of the above $LIBRARY_DIRS.)
# USE_PKG_CONFIG := 1

BUILD_DIR := build
DISTRIBUTE_DIR := distribute

# Uncomment for debugging. Does not work on OSX due to https://github.com/BVLC/caffe/issues/171
# DEBUG := 1

# The ID of the GPU that 'make runtest' will use to run unit tests.
TEST_GPUID := 0

# enable pretty build (comment to see full commands)
Q ?= @
```

*   关于cudnn的问题:由于faster-rcnn项目中使用的caffe版本过于古老,在cudnn兼容性上有一定问题,解决方法在后面会介绍
*   WITH\_PYTHON\_LAYER这一项需要,取消注释
*   注意:INCLUDE\_DIRS和LIBRARY\_DIRS需要手动添加内容,为了让ld找到hdf5

*   一波操作解决编译问题

```
cd ${你的py-fast-rcnn}/caffe-fast-rcnn
make -jx && make pycaffe -j3
```

(其中x为几都行)

*   当然这里可以使用cmake,cmake配置比较繁琐,这里我们选择避开它

*   如果编译成功,会不显示任何错误信息地结束,如果没有成功显示了相关错误信息,多半是可以通过apt install解决的问题,下面介绍几个apt install解决不了的问题的解法:
    
    *   ld: cannot find lcodec 这样的毛病 将_Makefile_的LIBRARIES加上opencv\_highgui opencv\_core opencv\_imgproc opencv\_codec

## 针对cudnnv5.1的适配

由于py-fast-rcnn项目发布的时候cudnn只有4,而且不知道英伟达的工程师是如何考虑的,cudnn升级竟然连接口都随便改,这里改法也比较简单

*   下载最新的caffe： git clone [https://github.com/BLVC/caffe.git](https://github.com/BLVC/caffe.git)
    
*   把${你的py-faster-rcnn目录}/caffe-fast-rcnn/src/caffe/layer/cudnn\_\*全部替换成最新的caffe-master中的相应目录中的相应文件
    
    *   替换${你的py-faster-rcnn目录}/caffe-fast-rcnn/include/caffe/util/cudnn.h
        
    *   最少替换如下cudnn\_\*文件：
        
        ${你的py-faster-rcnn目录}/src/caffe/layers：
        
        *   cudnn\_tanh\_layer.cpp & cu
        *   cudnn\_sigmoid\_layer.cpp & cu
        *   cudnn\_relu\_layer.cpp & cu
        
        ${你的py-faster-rcnn目录}/caffe-fast-rcnn/include/caffe/layers:
        
        *   cudnn\_tanh\_layer.hpp
        *   cudnn\_sigmoid\_layer.hpp
        *   cudnn\_relu\_layer.hpp
*   如果担心适配性问题，可以把所有含有cudnn的文件统统替换掉，包括include目录下和src目录下
    

## 训练网络

使用${你的py-faster-rcnn目录}/experiments/scripts/faster\_rcnn\_alt\_opt.sh进行训练，参数如下

*   $1: gpu序号——使用第几个显卡
*   $2: 网络模型——有ZF和VGG16供选择
*   $3：数据集——该脚本默认只支持pascal\_voc,即VOC2007数据集

## 运行时问题

*   TypeError: slice indices must be integers or None or have an \_\_index\_\_ method
    
    *   修改脚本，将${你的py-faster-rcnn目录}/tools/lib/minibatch.py的177行开始的循环，将其中ind,end,start变量使用int()转换为整型
*   Merge(...)：AttributeError: 'module' object has no attribute 'text\_format'
    
    *   修改脚本，在train.py中靠上部位加入import google.protobuf.text\_format

## 依旧没有解决的问题

当前安装出来的py-faster-rcnn可以测试网络，但是训练的时候会出现CURAND\_CHECK失败(201 vs. 0)