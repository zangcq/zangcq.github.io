---
title: caffe-ssd bug 解决日志
tags:
  - deeplearning
id: '455'
categories:
  - - 机器学习
date: 2017-11-16 20:56:42
---

#### ０．SSD测试时出现

```shell

I1122 13:34:31.285167  2869 layer_factory.hpp:77] Creating layer input
I1122 13:34:31.285254  2869 net.cpp:100] Creating Layer input
I1122 13:34:31.285285  2869 net.cpp:408] input -> data
F1122 13:34:37.337718  2869 syncedmem.hpp:18] Check failed: error == cudaSuccess (30 vs. 0)  unknown error
*** Check failure stack trace: ***
    @       0x7fb1bb1718  google::LogMessage::Fail()
    @       0x7fb1bb3614  google::LogMessage::SendToLog()
    @       0x7fb1bb1290  google::LogMessage::Flush()
    @       0x7fb1bb3eb4  google::LogMessageFatal::~LogMessageFatal()
    @       0x7fb1e53068  caffe::SyncedMemory::mutable_cpu_data()
    @       0x7fb1fe87f0  caffe::Blob<>::Reshape()
    @       0x7fb1fe8d54  caffe::Blob<>::Reshape()
    @       0x7fb1e78e54  caffe::InputLayer<>::LayerSetUp()
    @       0x7fb1fd7c54  caffe::Net<>::Init()
    @       0x7fb1fd99ac  caffe::Net<>::Net()
    @           0x408f6c  Detector::Detector()
    @           0x4058e4  main
    @       0x7fb141e8a0  __libc_start_main
Aborted (core dumped)
```

**解决方法**

**`sudo` 运行起来！！！**

#### 1.`hdf5`文件目录找不到

`src/caffe/net.cpp:8:18: fatal error: hdf5.h: 没有那个文件或目录`

> [https://github.com/NVIDIA/DIGITS/issues/156](https://github.com/NVIDIA/DIGITS/issues/156)
> 
> [http://www.linuxdiyf.com/linux/21717.html](http://www.linuxdiyf.com/linux/21717.html)

*   如果从lib中找到`hdf`相关文件

通过新建软链接来使`hdf5.h` 生效。

```shell

cd /usr/lib/x86_64-linux-gnu
#建立软链接
sudo ln -s libhdf5_serial.so.100.0.1 libhdf5.so
sudo ln -s libhdf5_serial_hl.so.100.0.0 libhdf5_hl.so
```

修改 `～/caffe/Makefile.config`

```shell

INCLUDE_DIRS := $(PYTHON_INCLUDE) /usr/local/include /usr/include/hdf5/serial/
LIBRARY_DIRS := $(PYTHON_LIB) /usr/local/lib /usr/lib /usr/lib/x86_64-linux-gnu/hdf5/serial/
```

*   如果没有安装的话，请如下操作

```shell

// install 
sudo apt-get install libhdf5-10 libhdf5-serial-dev libhdf5-dev libhdf5-cpp-11
// config path
find /usr -iname "*hdf5.h*"
/usr/include/hdf5/serial/hdf5.h
export CPATH="/usr/include/hdf5/serial/"
```

#### 2.找不到 `-lopenblas`

`/usr/bin/ld: 找不到 -lopenblas collect2: error: ld returned 1 exit status`

> [https://stackoverflow.com/questions/32353509/usr-bin-ld-cannot-find-lopenblas-error-in-caffe-compilation](https://stackoverflow.com/questions/32353509/usr-bin-ld-cannot-find-lopenblas-error-in-caffe-compilation)

可能`openblas`未安装，或者没有建立软链接

*   安装`openblas`
    
    ```bash
    sudo apt install liblapack-dev liblapack3 libopenblas-base libopenblas-dev
    ```
    

或者软链接为正常建立

*   建立软链接
    
    ```shell
    ln -s /opt/OpenBLAS/lib/libopenblas.so /usr/lib/libopenblas.so
    ```
    

#### 3.boost 未定义的引用

```shell

build_release/lib/libcaffe.so：对‘boost::re_detail_106200::cpp_regex_traits_implementation<char>::transform(char const, char const) const’未定义的引用
build_release/lib/libcaffe.so：对‘boost::re_detail_106200::cpp_regex_traits_implementation<char>::transform_primary(char const, char const) const’未定义的引用
collect2: error: ld returned 1 exit status
```

> [https://www.bountysource.com/issues/44327039-compile-issue-about-boost-and-cv](https://www.bountysource.com/issues/44327039-compile-issue-about-boost-and-cv)
> 
> [https://www.questarter.com/q/error-in-compiling-caffe-on-ubuntu-17-04-27\_46691614.html](https://www.questarter.com/q/error-in-compiling-caffe-on-ubuntu-17-04-27_46691614.html)
> 
> [https://stackoverflow.com/questions/17588440/cannot-link-boost-regex](https://stackoverflow.com/questions/17588440/cannot-link-boost-regex)

解决方案：

修改Makefile ,line181

加入boost\_regex

but 无效

Add `boost_regex` to `LIBRARIES` variable in Makefile in case you use Makefile.config compilation, or to `find_package(Boost 1.54 REQUIRED COMPONENTS system thread filesystem)` line in caffe/cmake/Dependencies.cmake

#### unsolved

> [https://bbs.archlinux.org/viewtopic.php?id=223497](https://bbs.archlinux.org/viewtopic.php?id=223497)最后

放弃治疗了。。重新装上原版的caffe。。。