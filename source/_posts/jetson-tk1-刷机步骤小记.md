---
title: Jetson TK1 刷机步骤小记
tags:
  - CUDA
  - GPU
  - Linux
id: '108'
categories:
  - - gpu-computing
    - Jetson TX1-2
date: 2017-06-19 09:34:21
---

### Jetson TK1 刷机步骤小记

英伟达出了三款嵌入式的开发板，TK1，TX1，TX2，分别对应Kepler ，Maxwell，Pascal架构。

本文呢讲具体怎么给Jetson TK1 刷机，以上的讨论呢，另写文章讨论。

### overview

先说一下原理，个人理解：

其实这个开发板呢，应该说是一个板卡电脑，可以装Linux系统，还有很多接口，虽然资源少了点，跟电脑有什么区别吗？

那么给它刷机呢，跟手机刷机，给你的电脑就装个系统营养，其实就这么简单。

### 1.下载资源

英伟达提供了安装套件，可以从下边这个链接download。

> [https://developer.nvidia.com/embedded/develop/software](https://developer.nvidia.com/embedded/develop/software)

这个呢是三款 开发板 的综述，可以都了解一下，这次我们要看第三个，也就是TK1这个。

既然是装系统，那么我们得有系统镜像，驱动什么的吧，好

在下边可以找到

下载链接如下

*   Driver : [Tegra124_Linux\_R21.5.0_armhf.tbz2](http://developer2.download.nvidia.com/embedded/L4T/r21_Release_v5.0/Tegra124_Linux_R21.5.0_armhf.tbz2?I6GLwc9JklE8PWY8SLWyXpvqlign20NZU45ltvNx2k1s62uwing19V-H8YGnrzbn17Tt2CZ_MxO9Faprk7Umu1ti2mIqKzzvJ-L3Bger_EJN6QV0ofHZFjNC8CSQ27eMy7iplgKbCqgLJ46gR1Q-DxOlctbLIQ599JTfbT6x)

*   [Simple file system : Tegra\_Linux\_Sample-Root-Filesystem\_R21.5.0\_armhf.tbz2](http://developer2.download.nvidia.com/embedded/L4T/r21_Release_v5.0/Tegra_Linux_Sample-Root-Filesystem_R21.5.0_armhf.tbz2?OfZ29i_EPz_XZO5lDScLJYtIKlW4y6Dbzbv5DxdbK5PgdW0U2YTHRYumZ4Ir3CGAFDXlA4vAZpsIlKGeaXmowf8QT9Es3ewiwr5HCnO_aLwjAf1uVN5Mybo5PFv2dao_-7rmlu-7W3C1PBQk42bRNal2jGW-NFMY1hgWGjXdkCTElZVb-aTVnyQRYFv5mRfDXcM)

资源搞下来了，接下来就好说了。

### 2.硬件连接

1.  把TK1 电源插好；
2.  用板卡自带的数据线（一定要数据线，不能随便找个充电线，一般手机的数据线也可以，micro usb 的），将你的主机（ Linux 系统 ！）跟板卡连接起来。
3.  如果你在windows下，退而求其次，装个ubuntu 的虚拟机，然后设置一下usb连接。

### 3.开始刷机

*   解压 把两个包放在同一个文件夹下。
*   1\. 注意顺序 先解压 Driver sudo tar --numeric-owner -jxpf Tegra124Linux\_R\*armhf.tbz2 # \* represent 版本号 其实也可以右键点击，extract here 其实也差不多。 解压 出一个 Linux\_for\_Tegra，进入这个文件夹，里边包含很多源文件，计入rootfs，这个目录现在是空的，应该只有一个readme.txt，顾名思义，这个就是文件系统的根目录，
*   2\. 将文件系统 解压到 /Linux\_for\_Tegra/rootfs/ $$sudo tar --numeric-owner -jxpf ../../Tegra\_Linux\_Sample-Root-Filesystem\_\*\_armhf.tbz2 $$
*   生成 image 文件，也就相当于系统镜像吧

```

cd /Linux_for_Tegra
#执行脚本
sudo ./apply_binaries.sh  
```

*   进入TK1的 recovery 模式
    1.  开机 按一下 power 键 （最左边 ）
    2.  迅速按住（长按）recovery （最右边）
    3.  按一下 reset 键 （中间）
*   在 主机端 执行刷机脚本
    
    *   还是在 Linux\_for\_Tegra/
    *   `#执行 sudo ./flash.sh -S 8GiB jetson-tk1 mmcblk0p1`
    
    会弹出一个8.6 G大小的 usb 设备，主机的shell 终端会打印一些信息，无非就是一些copy 的信息。 其实你也可以打开这个 usb 设备（类似打开u盘），可以看到好多文件夹正在往上copy。 等copy完成了，也就是刷机完成了，连上显示器，重启就可以用了。
    *   其实这个过程跟Linux恢复系统是一个原理，就是把原来的文件，保留原来的格式，再恢复到硬盘。 ​