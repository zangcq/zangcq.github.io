---
title: caffe - goturn 安装问题汇总
tags: []
id: '461'
categories:
  - - 机器学习
date: 2017-11-17 19:39:33
---

### caffe - goturn 安装问题汇总

#### 1.caffe目录未找到

```shell

Caffe_DEFINITIONS is 
Caffe_DIR is /home/zagncq/benchmark/caffe-master/build/
Caffe_INCLUDE_DIRS is /home/zagncq/benchmark/caffe-master/include/caffe
CMake Error: The following variables are used in this project, but they are set to NOTFOUND.
Please set them or make sure they are set and tested correctly in the CMake files:
```

**修改 `～/GOTURN/cmake/Modules/FindCaffe.cmake`文件第5行，将caffe绝对路径加上即可。**

> [https://github.com/davheld/GOTURN/issues/4](https://github.com/davheld/GOTURN/issues/4)

#### 2\. 未找到 caffe.pb.h

$$/home/embedded/caffe/include/caffe/blob.hpp:9:34: fatal error: caffe/proto/caffe.pb.h: No such file or directory$$

解决方法：

**用`protoc`从`caffe/src/caffe/proto/caffe.proto`生成\`caffe.pb.h和caffe.pb.cc**\`

```shell

cd caffe/src/caffe/proto/
protoc --cpp_out=/home/yourdir/caffe/include/caffe/ caffe.proto #必须使用绝对路径
```

> [http://blog.csdn.net/xmzwlw/article/details/48270225](http://blog.csdn.net/xmzwlw/article/details/48270225)

#### 3.boost regex 问题

```shell

‘boost::re_detail_106200::cpp_regex_traits_implementation<char>::transform_primary(char const*, char const*) const’未定义的引用
```

#### 4.tx2 安装 opencv失败

```shell

sudo: unable to resolve host tegra-ubuntu
[sudo] password for nvidia: 
Reading package lists... Done
Building dependency tree       
Reading state information... Done
Some packages could not be installed. This may mean that you have
requested an impossible situation or if you are using the unstable
distribution that some required packages have not yet been created
or been moved out of Incoming.
The following information may help to resolve the situation:

The following packages have unmet dependencies:
 libopencv-dev : Depends: libopencv-core-dev (= 2.4.9.1+dfsg-1.5ubuntu1)
                 Depends: libopencv-ml-dev (= 2.4.9.1+dfsg-1.5ubuntu1)
                 Depends: libopencv-imgproc-dev (= 2.4.9.1+dfsg-1.5ubuntu1)
                 Depends: libopencv-video-dev (= 2.4.9.1+dfsg-1.5ubuntu1)
                 Depends: libopencv-objdetect-dev (= 2.4.9.1+dfsg-1.5ubuntu1)
                 Depends: libopencv-highgui-dev (= 2.4.9.1+dfsg-1.5ubuntu1)
                 Depends: libopencv-calib3d-dev (= 2.4.9.1+dfsg-1.5ubuntu1)
                 Depends: libopencv-flann-dev (= 2.4.9.1+dfsg-1.5ubuntu1)
                 Depends: libopencv-features2d-dev (= 2.4.9.1+dfsg-1.5ubuntu1)
                 Depends: libopencv-legacy-dev (= 2.4.9.1+dfsg-1.5ubuntu1)
                 Depends: libopencv-contrib-dev (= 2.4.9.1+dfsg-1.5ubuntu1)
                 Depends: libopencv-ts-dev (= 2.4.9.1+dfsg-1.5ubuntu1)
                 Depends: libopencv-photo-dev (= 2.4.9.1+dfsg-1.5ubuntu1)
                 Depends: libopencv-videostab-dev (= 2.4.9.1+dfsg-1.5ubuntu1)
                 Depends: libopencv-stitching-dev (= 2.4.9.1+dfsg-1.5ubuntu1)
                 Depends: libopencv-gpu-dev (= 2.4.9.1+dfsg-1.5ubuntu1)
                 Depends: libopencv-superres-dev (= 2.4.9.1+dfsg-1.5ubuntu1)
                 Depends: libopencv-ocl-dev (= 2.4.9.1+dfsg-1.5ubuntu1) but it is not going to be installed
                 Depends: libopencv2.4-java (= 2.4.9.1+dfsg-1.5ubuntu1) but it is not going to be installed
                 Depends: libopencv2.4-jni (= 2.4.9.1+dfsg-1.5ubuntu1) but it is not going to be installed
                 Depends: libcv-dev (= 2.4.9.1+dfsg-1.5ubuntu1)
                 Depends: libhighgui-dev (= 2.4.9.1+dfsg-1.5ubuntu1)
                 Depends: libcvaux-dev (= 2.4.9.1+dfsg-1.5ubuntu1)
```

**解决办法，缺啥装啥，**

```shell

sudo apt install libopencv-ocl-dev libopencv2.4-java libopencv2.4-jni
```

#### 5.waring 　it doesnt matter

```shell

/home/nvidia/GOTURN/src/native/vot.cpp: In member function ‘vot_region* VOT::vot_initialize()’:
/home/nvidia/GOTURN/src/native/vot.cpp:237:43: warning: ignoring return value of ‘__ssize_t getline(char**, size_t*, FILE*)’, declared with attribute warn_unused_result [-Wunused-result]
     getline(&linebuf, &linesiz, inputfile);
```

## 6.vot

```shell

libGOTURN.a(vot.cpp.o): In function `VOT::vot_initialize()':
vot.cpp:(.text+0x250): undefined reference to `trax_server_setup'
vot.cpp:(.text+0x264): undefined reference to `trax_server_wait'
vot.cpp:(.text+0x26c): undefined reference to `trax_image_get_path'
vot.cpp:(.text+0x288): undefined reference to `trax_server_reply'
vot.cpp:(.text+0x2bc): undefined reference to `trax_region_get_rectangle'
vot.cpp:(.text+0x2c4): undefined reference to `trax_region_release'
vot.cpp:(.text+0x2cc): undefined reference to `trax_image_release'
libGOTURN.a(vot.cpp.o): In function `VOT::vot_quit()':
vot.cpp:(.text+0x4a4): undefined reference to `trax_cleanup'
libGOTURN.a(vot.cpp.o): In function `VOT::vot_frame()':
vot.cpp:(.text+0x644): undefined reference to `trax_server_wait'
vot.cpp:(.text+0x658): undefined reference to `trax_image_get_path'
vot.cpp:(.text+0x66c): undefined reference to `trax_image_release'
libGOTURN.a(vot.cpp.o): In function `VOT::vot_report(vot_region*)':
vot.cpp:(.text+0x6f0): undefined reference to `trax_region_create_rectangle'
vot.cpp:(.text+0x704): undefined reference to `trax_server_reply'
vot.cpp:(.text+0x70c): undefined reference to `trax_region_release'
```

解决办法

*   **首先下载[trax](https://github.com/votchallenge/trax/),**
    
    `git clone https://github.com/votchallenge/trax.git`
    
*   **然后编译trax**
    
    ```shell
    
    cd trax
    mkdir build
    cd build 
    cmake ..
    make
    ```
    
*   **修改CMakeLists.txt of GOTURN around line 84:把trax的实际路径写上**
    
    ```shell
    
    #Note: If can't find trax, please download trax and build it, then uncomment the below line and set the path manually
    target_link_libraries(${PROJECT_NAME}home/your dir/trax/build/libtrax.so)
    ```
    

> [https://github.com/davheld/GOTURN/issues/1](https://github.com/davheld/GOTURN/issues/1)
> 
> [https://github.com/davheld/GOTURN/issues/39](https://github.com/davheld/GOTURN/issues/39)