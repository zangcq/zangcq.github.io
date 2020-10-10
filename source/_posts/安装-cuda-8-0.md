---
title: 安装 NVIDIA 驱动 和 CUDA 8.0
tags:
  - CUDA
  - Linux
  - Shell
id: '160'
categories:
  - - tools
    - 系统管理维护
date: 2017-07-06 21:09:44
---

### **1.卸载本机原有驱动，**

因为 通常ubuntu或者debian都是来自社区的驱动，并不是英伟达的官方驱动

如何完全 卸载 nvidia驱动 [http://forums.debian.net/viewtopic.php?f=10&t=55518](http://forums.debian.net/viewtopic.php?f=10&t=55518)

```c

aptitude purge ~i~nnvidia
```

### **2.从官网下载对应显卡驱动程序，进行安装**

#### 问题１　在装驱动之前退出Ｘ server

#### ERROR: You appear to be running an X server; please exit X before installing. For further details, please see the section INSTALLING THE NVIDIA DRIVER in the README available on the Linux driver

#### 解决办法：

```c++

1,ctrl+alt+f1进入tty1命令行界面

2,输入帐号密码登录

3,执行sudo /etc/init.d/lightdm stop

或者是sudo service lightdm stop

或者是sudo stop lightdm

4,ctrl+alt+f7检查图形界面是否被关闭？

5,安装你的驱动

6,执行sudo /etc/init.d/lightdm start或其他再次启动图形界
```

#### 问题２　退出Ｘ后，出现当前系统仍有

#### ERROR:the Nouveau kernel driver is currently in use by your system. .....

Nouveau kernel driver 这个驱动正在被系统使用,这个驱动和Nvidia驱动冲突,要想继续安装,则必须禁用此驱动！因为系统默认装的显卡驱动就是Nouveau .　

Nouveau是一个由爱好者组织的针对NVIDIA显卡开发第三方开源3D驱动的共同项目，并且Nouveau是在完全没有得到NVIDIA任何支持的情况下进行开发的，Nouveau算是X.Org基金会的一个项目

#### 解决办法：

```c++

sudo gedit /etc/default/grub
把 nomodeset 加到 GRUB_CMDLINE_LINUX 那一行如： 

GRUB_CMDLINE_LINUX="nomodeset"
然后终端运行： 

sudo update-grub
重启, 再安装NV驱动
```

总结自　13.10如何退出 X Server

> [http://www.ubuntukylin.com/ukylin/forum.php?mod=viewthread&tid=5629](http://www.ubuntukylin.com/ukylin/forum.php?mod=viewthread&tid=5629)

Nouveau kernel driver 说明引用自

> [http://enetq.blog.51cto.com/479739/591622](http://enetq.blog.51cto.com/479739/591622)

```c

//卸载英伟达驱动 
```

```c

nvidia-uninstall //即可
```

### **3.从官网下载 cuda 8.0**

直接安装 即可 **.run类型**

```c

直接运行.run文件
```

**.deb**

```c

sudo dpkg -i cuda-repo-ubuntu1604-8-0-local-ga2_8.0.61-1_amd64.deb
sudo apt-get update
sudo apt-get install cuda
```

**注意：**在安装的过程中可能会出现，gcc 版本过高的问题，那么我们就需要，对gcc 降级： 1）安装gcc/g++版本为4.9.x

```c

sudo apt-get install  gcc-4.9
sudo apt-get install  g++-4.9
```

2）链接gcc/g++实cd /usr/bin

```c

sudo rm gcc

sudo ln -s gcc-4.9 gcc

sudo rm g++

sudo ln -s g++-4.9 g++
```

### **4.cuda 环境变量配置**

```c

export PATH=/usr/local/cuda-8.0/bin:$PATH

export LD_LIBRARY_PATH=/usr/local/cuda-8.0/lib64:$LD_LIBRARY_PATH
```

### 5.如果出现 环境变量配置错误问题

应急

```c

在命令行中输入：export PATH=/usr/bin:/usr/sbin:/bin:/sbin:/usr/X11R6/bin
```

则参考

[http://blog.csdn.net/lancees/article/details/8031750](http://blog.csdn.net/lancees/article/details/8031750)

### 6\. Uninstallation

```c

To uninstall the CUDA Toolkit, run the uninstallation script provided in the bin 
directory of the toolkit. By default, it is located in /usr/local/cuda-8.0/bin:
**$ sudo /usr/local/cuda-8.0/bin/uninstall_cuda_8.0.pl**

To uninstall the NVIDIA Driver, run nvidia-uninstall:
**$ sudo /usr/bin/nvidia-uninstall**

Use the following commands to uninstall a RPM/Deb installation:

$ sudo yum remove <package_name>                      //Redhat/CentOS

$ sudo dnf remove <package_name>                      // Fedora

$ sudo zypper remove <package_name>                   // OpenSUSE/SLES

$ sudo apt-get --purge remove <package_name>          // Ubuntu
```

Read more at: [http://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html#ixzz4Z0rvSqpI](http://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html#ixzz4Z0rvSqpI) Follow us: @GPUComputing on Twitter NVIDIA on Facebook