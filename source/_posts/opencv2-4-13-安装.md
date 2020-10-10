---
title: openCV2.4.13 安装
tags: []
id: '494'
categories:
  - - 机器学习
date: 2017-12-20 11:56:53
---

## `openCV2.4.13` 安装

1.  下载并解压
    
    ```shell
    
    unzip opencv-2.4.13.zip
    ```
    
2.  进入`openCV`目录,建立`release`文件夹
    
    ```shell
    
    cd opencv-2.4.13
    mkdir release
    ```
    
3.  安装依赖库
    
    ```shell
    
    sudo apt-get install build-essential cmake libgtk2.0-dev pkg-config python-dev python-numpy libavcodec-dev libavformat-dev libswscale-dev 
    
    sudo apt-get install -x264 v4l-utils ffmpeg 
    ```
    
4.  进入`release`目录,`cmake`编译,把`lib`安装到 `/usr/local/`目录下
    
    ```shell
    
    cmake -D CMAKE_BUILD_TYPE=RELEASE  \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D WITH_TBB=ON \
    -D BUILD_NEW_PYTHON_SUPPORT=ON \
    -D WITH_V4L=ON \
    -D INSTALL_C_EXAMPLES=ON \
    -D INSTALL_PYTHON_EXAMPLES=ON \
    -D BUILD_EXAMPLES=ON \
    -D WITH_QT=ON \
    -D WITH_OPENGL=ON ..
    ```
    
5.  安装
    
    ```shell
    
    sudo make install
    ```
    

如果不想安装到`/usr/local`目录下的话,咋整?

1.  坑
    
    ```shell
    
    CMake Error at CMakeLists.txt:14 (find_package):
      By not providing "FindQt5Core.cmake" in CMAKE_MODULE_PATH this project has
      asked CMake to find a package configuration file provided by "Qt5Core", but
      CMake did not find one.
    
      Could not find a package configuration file provided by "Qt5Core"
      (requested version 5.0) with any of the following names:
    
        Qt5CoreConfig.cmake
        qt5core-config.cmake
    ```
    
    需要安装依赖 `Qt5Core`
    
    ```shell
    
    sudo apt install qtbase5-dev
    ```
    
    ​