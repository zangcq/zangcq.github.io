---
title: Caffe fast-rcnn 踩坑
tags: []
id: '873'
categories:
  - - 机器学习
date: 2019-07-10 10:08:37
---

\[TOC\]

### Caffe install in RadHat

官方教程

> https://caffe.berkeleyvision.org/installation.html

#### readme

```
git clone --recursive https://github.com/rbgirshick/py-faster-rcnn.git
$FRCN_ROOT = py-faster-rcnn

cd $FRCN_ROOT/lib
make

cd $FRCN_ROOT/caffe-fast-rcnn
# Now follow the Caffe installation instructions here:
#   http://caffe.berkeleyvision.org/installation.html

# If you're experienced with Caffe and have all of the requirements installed
# and your Makefile.config in place, then simply do:
make -j8 && make pycaffe
```

#### RHEL requires

> [http://caffe.berkeleyvision.org/install\_yum.html](http://caffe.berkeleyvision.org/install_yum.html)

```
sudo yum install protobuf-devel leveldb-devel snappy-devel opencv-devel boost-devel hdf5-devel

sudo yum install gflags-devel glog-devel lmdb-devel
# 依赖项未安装
protoc: Command not found
./include/caffe/util/mkl_alternate.hpp:11:19: fatal error: cblas.h: No such file or directory
```

如果失败，见链接手动安装

其他教程

> https://www.zybuluo.com/huynh/note/227144

#### Other dependency

*   CUDA 可暂时不开
*   Open BLAS install

```
  git clone https://github.com/xianyi/OpenBLAS.git
  cd OpenBLAS
  make -j4
  make install--

  配置一下 caffe 的makefile.config
  BLAS := open
  BLAS_INCLUDE :=  /opt/OpenBLAS/include
  BLAS_LIB := /opt/OpenBLAS/lib
```

[https://blog.csdn.net/quheDiegooo/article/details/53082809](https://blog.csdn.net/quheDiegooo/article/details/53082809)

*   Boost install

```
  tar xvf boost_1_56_0.tar.bz2
  cd boost_1_57_0/
  然后运行：
   ./bootstrap.sh --with-libraries=system,thread,python,filesystem
   ./b2
```

*   Pyconfig.h not such file `/usr/local/include/boost/python/detail/wrap_python.hpp:50:23: fatal error: pyconfig.h: No such file or directory`
*   `sudo yum install python-devel.x86_64`

> https://github.com/BVLC/caffe/issues/410

*   hdf5源码安装 `No match for argument: hdf5-devel Error: Unable to find a match: hdf5-devel` download hdf5
*   check 一下version
*   Headers are 1.8.18, library is 1.8.12
*   `https://www.hdfgroup.org/downloads/hdf5/` install

> https://blog.csdn.net/luoying\_1993/article/details/53228473

*   ImportError: No module named **skimage.io**
*   `sudo pip install scikit-image`

```
  Installing collected packages: pyparsing, backports.functools-lru-cache, subprocess32, pytz, python-dateutil, kiwisolver, cycler, matplotlib, scikit-image

  Cannot uninstall 'pyparsing'.
  # 安装较新的版本
  sudo pip install -I pyparsing==2.2.0
```

> https://blog.huihut.com/2018/10/13/PyparsingFailsToUninstallCausingErrorInInstallingMatplotlib/
> 
> https://github.com/yahoo/open\_nsfw/issues/13

*   numpy 版本过低 如果卸载不掉，直接强行删掉 sudo rm -rf /usr/lib64/python2.7/site-packages/numpy\* 一种方法是直接升级，但是可能会失败 sudo pip install -U numpy 另一种方法直接安装 特定版本，成功率比较高 $sudo pip install -U numpy==1.12.0
*   leveldb 手动安装1.7.0版本

```
  https://www.cnblogs.com/Crysaty/p/6272994.html
```

*   手动安装opencv https://blog.csdn.net/antony1776/article/details/73528028 手动安装opencv ，然后拷贝到python库中

```
  wget https://github.com/opencv/opencv/archive/2.4.13.zip

  cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D BUILD_NEW_PYTHON_SUPPORT=ON -D BUILD_EXAMPLES=ON .
  make
  make install

  cp ./lib/cv2.so /usr/lib/python2.7/site-packages/
  cp ./modules/python/src2/cv.py /usr/lib/python2.7/site-packages/
```

*   可能依赖的python模块
*   ImportError: No module named easydict Cpython `sudo yum install Cython` `sudo pip install easydict`
*   ImportError: No module named google.protobuf.internal `sudo pip install protobuf`
*   ImportError: No module named google.protobuf.internal ​ `sudo yum install tkinter`

> https://stackoverflow.com/questions/36327134/matplotlib-error-no-module-named-tkinter

*   No module named cv2 `sudo pip install opencv-python` https://stackoverflow.com/questions/19876079/cannot-find-module-cv2-when-using-opencv 手动安装opencv即可

> https://blog.csdn.net/u010668907/article/details/51112899

*   need caffe

```
  Traceback (most recent call last):
    File "./tools/demo.py", line 18, in <module>
      from fast_rcnn.test import im_detect
    File "/data/home/lingyao.zcq/py-faster-rcnn/tools/../lib/fast_rcnn/test.py", line 16, in <module>
      import caffe
```

*   手动安装libglog `/usr/local/lib/libglog.a: error adding symbols: Bad value collect2: error: ld returned 1 exit status`

```
  CXXFLAGS="-O3 -fPIC" ./configure
  安装目录 
  /usr/bin/install

  wget https://storage.googleapis.com/google-code-archive-downloads/v2/code.google.com/google-glog/glog-0.3.3.tar.gz
  tar zxvf glog-0.3.3.tar.gz
  cd glog-0.3.3
  #./configure
  ./configure CXXFLAGS=-fPIC
  make && sudo make install

  再看一是否需要拷贝到/usr/lib
```

*   需要使用 -fPIC 重新编译
*   类似问题 可能出现在 protobuf/gflags/glog 下载源码，添加CFLAG="-fPIC"进行编译

> https://blog.csdn.net/h\_jlwg6688/article/details/52410959
> 
> https://stackoverflow.com/questions/33634711/caffe-recompile-with-fpic-libglog-a-error
> 
> https://www.cnblogs.com/youxin/p/5086937.html
> 
> https://www.cnblogs.com/xiehongfeng100/p/4375613.html

*   make runtest 出错  
    已解决，需要添加环境变量

```
  export LD_LIBRARY_PATH=/usr/local/OpenBlas/lib:$LD_LIBRARY_PATH

  export LD_LIBRARY_PATH=/home/lingyao.zcq/caffe_depend_opt/OpenBLAS/lib:$LD_LIBRARY_PATH
  # hdf5
  export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
  Warning! ***HDF5 library version mismatched error***

  # level db
  export LD_LIBRARY_PATH=/usr/lib:$LD_LIBRARY_PATH
  export LD_LIBRARY_PATH=/home/lingyao.zcq/depend/protobuf:$LD_LIBRARY_PATH


  down vote accepted I added the line －>     
  /usr/local/lib to /etc/ld.so.conf 
  and then ran sudo ldconfig.   
  Problem solved.
```

*   make lib dir first

[https://github.com/rbgirshick/py-faster-rcnn/issues/8](https://github.com/rbgirshick/py-faster-rcnn/issues/8)

*   Nvidia 驱动安装

```
  Edit /etc/default/grub. Append the following  to “GRUB_CMDLINE_LINUX”
  rd.driver.blacklist=nouveau nouveau.modeset=0

  vim /etc/default/grub
  find 
  “GRUB_CMDLINE_LINUX”
  add 
  rd.driver.blacklist=nouveau nouveau.modeset=0

  vim etc/modprobe.d/blacklist.conf 
  blacklist nouveau

  Generate a new grub configuration to include the above changes.
  grub2-mkconfig -o /boot/grub2/grub.cfg

  Edit/create /etc/modprobe.d/blacklist.conf and append:
  blacklist nouveau

  (*optional*)Backup your old initramfs and then build a new one
  mv /boot/initramfs-$(uname -r).img /boot/initramfs-$(uname -r)-nouveau.img
  dracut /boot/initramfs-$(uname -r).img $(uname -r)

  Reboot your machine


  nvidia              16594374  21
  ipmi_msghandler        46609  3 ipmi_devintf,nvidia,ipmi_si
  i2c_core               40582  7 ast,drm,igb,i2c_i801,drm_kms_helper,i2c_algo_bit,nvidia


  lsmod  grep  nvidia
  nvidia_drm             19164  0
  nvidia_modeset       1036498  1 nvidia_drm
  nvidia_uvm            782669  0
  nvidia              16594374  23 nvidia_modeset,nvidia_uvm
  ipmi_msghandler        46609  3 ipmi_devintf,nvidia,ipmi_si
  drm                   349262  5 ast,ttm,drm_kms_helper,nvidia_drm
  i2c_core               40582  7 ast,drm,igb,i2c_i801,drm_kms_helper,i2c_algo_bit,nvidia

  To see who are using nvidia: sudo lsof  grep nvidia
  then stop services or processes using nvidia
```

[https://www.linuxquestions.org/questions/linux-kernel-70/how-to-force-remove-a-kernel-module-686210](https://www.linuxquestions.org/questions/linux-kernel-70/how-to-force-remove-a-kernel-module-686210/)

#### Usage

```
cd caffe_faster_rcnn_quantize

# compile lib
cd lib
make -j
cd ../

# compile caffe
cd caffe-fast-rcnn
make -j && make pycaffe


cd caffe_faster_rcnn_quantize
# 替换的net.cpp
# 重新make -j && make pycaffe
# 2d model

# run demo
$python quantize_pose/demo_inference.py ../faster_.prototxt ../faster_.caffemodel --images_path_list poselist.txt --images_root_folder ./posetest/

# --images_path_list   图片列表保存图片路径的list
# --images_root_folder 真是图片存放的文件夹 ./posetest/
```