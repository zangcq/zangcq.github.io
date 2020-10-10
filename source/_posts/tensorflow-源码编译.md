---
title: TensorFlow 源码编译
tags: []
id: '1391'
categories:
  - - 机器学习
comments: false
date: 2020-08-07 14:38:37
---

TensorFlow 源码编译构建 大型工程编译坑还是太多，这波先把坑给大家踩一踩。

# Reference

主要参考tensorflow官方网站和自己之前的一些经验吧。

> [https://www.tensorflow.org/install/source](https://www.tensorflow.org/install/source)

这次主要是在物理机上搞的，既然公司有容器化的战略，那么下一步全部上容器，云化。

# 依赖安装

像tensorflow这种工程的安装，主要是版本依赖的问题居多，那么我先把我在版本依赖的坑写一下。

*   Python 版本 3.6.9

*   Pip list

1.  Numpy 1.19.1

1.  Wheel 0.34.2

不支持在 Doc 外粘贴 block**参考一下我的配置**

*   Bazel 版本

*   我刚开始用了 0.24.1, 有些坑，后来改成0.26.1搞定了。

*   Tensorflow 用 bazel来做构造工具，其性质跟 blade是一样的。

*   我们可以通过 cat 一下 configure.py 这个文件来查看一下，你需要哪个版本，然后对应安装即可。

```
cd tensorflow
cat configure.py  grep BAZEL_VERSION
_TF_MIN_BAZEL_VERSION = '0.24.1'
_TF_MAX_BAZEL_VERSION = '0.26.1'
```

*   直接到release网页下载下来，然后进行安装，（服务器可能会预装 bazel，但是版本可能会有点高）

```
https://github.com/bazelbuild/bazel/releases
https://github.com/bazelbuild/bazel/releases/tag/0.26.1
wget https://github.com/bazelbuild/bazel/releases/download/0.26.1/bazel-0.26.1-installer-linux-x86_64.sh
```

*   然后把bazel 安装在自己的目录，使能一下PATH

```
chmod a+x bazel-0.24.1-installer-linux-x86_64.sh
./bazel-0.24.1-installer-linux-x86_64.sh --prefix=/path/to/you
export PATH=/data01/zangchuanqi/bin:$PATH
```

*   GCC 版本

*   GCC 版本也有点曲折，之前用的是4.9.2也就是系统默认版本

*   但是中间eigen（CPU线性代数加速库）需要5.x以上的版本来编译，所以换成5.3，然后又有bug。最终我用了7.3.0编译成功的，再试一下8.3.0吧。

*   以上版本都是gcc官方的release

*   有一些坑，我记录在这儿了。 [源码编译GCC（我的博客）](http://www.zangcq.com/2020/08/03/源码编译gcc/)

基本需要的依赖都安装完了的话，下边在安装，就十分顺滑了。

# 安装TensorFlow

*   配置

```
cd tensorflow
./configure
```

*   说明一下，常规操作一般只需要CPU的话，就无需选择 XLA 选项和CUDA开关，但是一般有GPU加速的需求，就需要按照我的这个配置来。

*   这是一个交互式的脚本文件，所以呢，就是需要填Y或者N，然后也需要填一下 CUDA路径，这根据你所需要的版本来定。

*   仔细看一下我的选择

*   Python 环境，选择了自己的virtual环境

*   XLA 选择Y

*   CUDA的选的10

*   CUDNN选的7

*   CUDA PATH 手动选了/data01/zangchuanqi/workspace/cuda

*   Clang 不选了

*   GCC 选了自定义的7.3.0 /data01/zangchuanqi/gcc-7.3.0/build/install/bin/gcc

*   其他的就default了

```shell
(tvm.venv) zangchuanqi@n22-145-158:~/workspace/tensorflow$ ./configure
WARNING: --batch mode is deprecated. Please instead explicitly shut down your Bazel server using the command "bazel shutdown".
You have bazel 0.24.1 installed.
Please specify the location of python. [Default is /data01/zangchuanqi/tvm.venv/bin/python]:
Found possible Python library paths:
 /data01/zangchuanqi/tvm.venv/lib/python3.6/site-packages
 /data01/zangchuanqi/workspace/tvm/topi/python
 /data01/zangchuanqi/workspace/tvm/python
Please input the desired Python library path to use.  Default is [/data01/zangchuanqi/tvm.venv/lib/python3.6/site-packages]
Do you wish to build TensorFlow with XLA JIT support? [Y/n]: y
XLA JIT support will be enabled for TensorFlow.
Do you wish to build TensorFlow with OpenCL SYCL support? [y/N]: n
No OpenCL SYCL support will be enabled for TensorFlow.
Do you wish to build TensorFlow with ROCm support? [y/N]: n
No ROCm support will be enabled for TensorFlow.
Do you wish to build TensorFlow with CUDA support? [y/N]: Y
CUDA support will be enabled for TensorFlow.
Do you wish to build TensorFlow with TensorRT support? [y/N]: n
No TensorRT support will be enabled for TensorFlow.
Could not find any cudnn.h matching version '' in any subdirectory:
    ''
    'include'
    'include/cuda'
    'include/*-linux-gnu'
    'extras/CUPTI/include'
    'include/cuda/CUPTI'
of:
    '/lib'
    '/lib/x86_64-linux-gnu'
    '/lib32'
    '/libx32'
    '/opt/tiger/ss_lib/so'
    '/usr'
    '/usr/lib'
    '/usr/lib/x86_64-linux-gnu'
    '/usr/lib/x86_64-linux-gnu/libfakeroot'
    '/usr/local/cuda'
    '/usr/local/cuda/lib64'
    '/usr/local/cudnn/lib64'
Asking for detailed CUDA configuration...
Please specify the CUDA SDK version you want to use. [Leave empty to default to CUDA 10]: 10
Please specify the cuDNN version you want to use. [Leave empty to default to cuDNN 7]: 7
Please specify the locally installed NCCL version you want to use. [Leave empty to use http://github.com/nvidia/nccl]:
Please specify the comma-separated list of base paths to look for CUDA libraries and headers. [Leave empty to use the default]: /data01/zangchuanqi/workspace/cuda
Found CUDA 10.0 in:
  /data01/zangchuanqi/workspace/cuda/lib64
  /data01/zangchuanqi/workspace/cuda/include
Found cuDNN 7 in:
  /data01/zangchuanqi/workspace/cuda/lib64
  /data01/zangchuanqi/workspace/cuda/include
Please specify a list of comma-separated CUDA compute capabilities you want to build with.
You can find the compute capability of your device at: https://developer.nvidia.com/cuda-gpus.
Please note that each additional compute capability significantly increases your build time and binary size, and that TensorFlow only supports compute capabilities >= 3.5 [Default is: 7.0,7.0,7.0,7.0,7.0,7.0,7.0,7.0]:
Do you want to use clang as CUDA compiler? [y/N]:
nvcc will be used as CUDA compiler.
Please specify which gcc should be used by nvcc as the host compiler. [Default is /usr/bin/gcc]:/data01/zangchuanqi/gcc-7.3.0/build/install/bin/gcc
Do you wish to build TensorFlow with MPI support? [y/N]: n
No MPI support will be enabled for TensorFlow.
Please specify optimization flags to use during compilation when bazel option "--config=opt" is specified [Default is -march=native -Wno-sign-compare]:
Would you like to interactively configure ./WORKSPACE for Android builds? [y/N]: n
Not configuring the WORKSPACE for Android builds.
Preconfigured Bazel build configs. You can use any of the below by adding "--config=<>" to your build command. See .bazelrc for more details.
    --config=mkl         # Build with MKL support.
    --config=monolithic      # Config for mostly static monolithic build.
    --config=gdr         # Build with GDR support.
    --config=verbs        # Build with libverbs support.
    --config=ngraph        # Build with Intel nGraph support.
    --config=numa         # Build with NUMA support.
    --config=dynamic_kernels     # (Experimental) Build kernels into separate shared objects.
    --config=v2          # Build TensorFlow 2.x instead of 1.x.
Preconfigured Bazel build configs to DISABLE default on features:
    --config=noaws        # Disable AWS S3 filesystem support.
    --config=nogcp        # Disable GCP support.
    --config=nohdfs        # Disable HDFS support.
    --config=noignite       # Disable Apache Ignite support.
    --config=nokafka       # Disable Apache Kafka support.
    --config=nonccl        # Disable NVIDIA NCCL support.
Configuration finished
```

*   编译安装

*   Bazel 构建

*   生成wheel包到../work/tensorflow\_pkg

*   Pip 安装 到当前环境

*   参数说明

*   Opt 使能优化

*   Cuda 使能GPU

```
bazel build --config=opt --config=cuda //tensorflow/tools/pip_package:build_pip_package
./bazel-bin/tensorflow/tools/pip_package/build_pip_package ../work/tensorflow_pkg
pip install ../work/tensorflow_pkg/tensorflow-version-tags.whl
```

*   Have a Test

```
(test.venv) zangchuanqi@n22-145-158:~$ python
Python 3.6.9 Anaconda, Inc. (default, Jul 30 2019, 19:07:31)
[GCC 7.3.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import tensorflow as tf
>>> print tf.__version__
 File "<stdin>", line 1
  print tf.__version__
      ^
SyntaxError: Missing parentheses in call to 'print'. Did you mean print(tf.__version__)?
>>> print (tf.__version__)
1.15.3
```

大功告成！

# 使能XLA

> *   [https://tensorflow.juejin.im/performance/xla/jit.html](https://tensorflow.juejin.im/performance/xla/jit.html)

A. 环境变量设置 ![img](https://bytedance.feishu.cn/space/api/box/stream/download/asynccode/?code=0442ec937ae3220319741e4446b78a22_8f118824ce50c961_boxcncC7ORaBZjdHsistALqwgXc_q3GgiSBLKXrh2bNcvxgyq5cRe5nLOe4h)

```
# XLA FLAGS
export XLA_FLAGS="--xla_hlo_profile --xla_dump_to=/tmp/foo --xla_dump_hlo_as_text --xla_dump_hlo_as_dot --xla_dump_hlo_as_html --xla_dump_hlo_as_proto"
# 输出所有的hlo pass
export XLA_FLAGS="--xla_hlo_profile --xla_dump_hlo_pass_re=.* --xla_dump_to=./test_dump --xla_dump_hlo_as_dot"
# log 选项
export TF_CPP_MIN_VLOG_LEVEL=4
export TF_CPP_MIN_LOG_LEVEL=0
```

![img](https://bytedance.feishu.cn/space/api/box/stream/download/asynccode/?code=89694b1565bdf03d22eeccc09f9c660d_8f118824ce50c961_boxcnF651qvqVX87Ac2ZgL9dfic_dJEgUXhX6nteS1tAs2ajzsemU2DKV25n) B. 代码case

*   [https://github.com/tensorflow/tensorflow/blob/master/tensorflow/examples/tutorials/mnist/mnist\_softmax\_xla.py](https://github.com/tensorflow/tensorflow/blob/master/tensorflow/examples/tutorials/mnist/mnist_softmax_xla.py)

C. 结果查看 ![img](https://bytedance.feishu.cn/space/api/box/stream/download/asynccode/?code=1ddf1e0e223d0bcab4bae76cdb8fed0a_8f118824ce50c961_boxcn85q65Txptj9LrmKkOeUvRd_097jHmUSylUhBoyHcTp7CsQ8iDGsUp5Z)

*   生成的图如下

*   优化前的

![img](https://bytedance.feishu.cn/space/api/box/stream/download/asynccode/?code=902ea21155bbc5fd29f6a0e9f1cec400_8f118824ce50c961_boxcnbvkplDqji8ThfGX98pJGFb_ZzOYfPkpUaxuXxIqysCa0TKGdZTvJ7Nd)

*   优化后

![img](https://bytedance.feishu.cn/space/api/box/stream/download/asynccode/?code=e94edc569c59fdfee59604354d0e68ba_8f118824ce50c961_boxcnWlU76jzIv4u5DHa1LCOzrf_RCFGhgIU93DYUcFNmIBpZuo7qcRFyJ6i)