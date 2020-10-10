---
title: windows 和 Linux 系统 从硬盘迁移到SSD
tags:
  - Linux
  - Shell
id: '150'
categories:
  - - tools
    - 系统管理维护
date: 2017-07-06 20:53:21
---

# windows 和 Linux 系统 从硬盘迁移到SSD

## 1\. Windows

实验室这次搞了几块三星的ssd，型号是：三星(SAMSUNG) 850 EVO 250G SATA3 固态硬盘  
三星有个sangsung magician 的软件，可以直接支持系统拷贝，这次就不细说 详见如下链接：

> [http://ssd.zol.com.cn/418/4186614.html](http://ssd.zol.com.cn/418/4186614.html)

时隔半年，老板有钱了，又搞了一批，但是似乎软件不能用了，尴尬。

## 2\. Ubuntu

大家装系统一般都会做一个u盘镜像之类的东西吧，简单一说 安装镜像 `*.iso` ,用镜像工具ultra ISO，写入U盘，那么我们就做成了一个`liveCD`。

以下工作我们就是在 `liveCD`中做的。

首先获得`liveCD`的root 权限

```shell

sudo su
```

1.  其实原理很简单，划好分区，直接从机械盘，复制到`ssd`就好了。。。
2.  然后把grub对应修改就好了；

中间出了个小插曲，浪费了大好时间

之前写的太粗略了，今天详细写：

### 2.1 ubuntu分区工具 gparted

一般ubuntu 或者都会自带 gparted 分区工具，gparted 是一个图形化界面工具，

其实跟windows磁盘管理或者disk genius 有些类似，我们可以很灵活的进行分区划分。

划分后会有自己的新的uuid 号，或者称为磁盘号。

我们可以通过命令

```shell

sudo blkid #查看分区表
```

### 2.2 磁盘文件拷贝

两条路择其一。

#### 2.2.1 操作系统 层 `cp`命令

我们可以先挂载需要拷贝的磁盘，然后进行拷贝

```shell

#新建两个文件夹，名字根据自己习惯命名
sudo  mkdir  /mnt/sdamnt  
sudo  mkdir  /mnt/sdbmnt 

#将需要的磁盘 挂载的临时新建的文件夹
sudo mount  /dev/sda1    /mnt/sdamnt
sudo mount  /dev/sdb1    /mnt/sdbmnt

#cp 将 文件数据 拷贝到目标文件。
sudo cp -ax  /mnt/sdamnt/*  /mnt/sdbmnt/*
#需要等待。。。
#-ax 表示所有的文件类型都保持原来的类型不变。
```

*   ax选项很重要！！

如果多个分区，比如有 / ，/boot， /home 两种思路，

1.  按照原来分区分别copy
2.  只划分 / 分区，然后讲 /boot ，/home 分别拷贝到相对应的文件夹。

### 2.2.2 磁盘层 dd

一条命令很简单

```shell

#sdb1 源磁盘   
#sda1 目标磁盘

dd if=/dev/sdb1 of=/dev/sda1 
```

拷贝时查看速度

```shell

watch -n 5 killall -USR1 dd
```

#### 备注：

注意dd命令也会拷贝uuid过去，意味着，`/dev/sda1`的uuid和`/dev/sdb1`的uuid是一样的。

`uuid`是一个唯一的标识符，因为类似`/dev/sda`这样的映射点，在新设备加入的时候，可能会生成新的映射点，比如原来系统里是`/dev/sda`现在变成了`/dev/sdb`等等，所以一般情况下，在`/etc/fstab`里写自己规则的时候，都是用uuid而非映射点。

可以不修改新硬盘分区的uuid，也就省去了修改`/etc/fstab`或者`/boot/grub/grub.conf`的麻烦。

由于拷贝的原因，之前分区的uuid 也变成现在的uuid 了。不管那种我们的grub 都需要修复

## 3.grub修复

拷贝的过程简单，但是耗时间很长，一般分区没有什么错误是没问题的，那么经常的大坑一般都在grub这。

如果重启之后无法进入系统，那么我们需要修复grub。

## 3.1 手动修复`/etc/fstab 和 boot/grub/grub.cfg`

这种方式适合老手，新手略过，但是作为我来讲有时也不一定能成功。

[http://blog.csdn.net/dark5669/article/details/52551583](http://blog.csdn.net/dark5669/article/details/52551583)

## 3.2 使用grub-repair 工具

安装 boot-repair

```shell

sudo add-apt-repository ppa:yannubuntu/boot-repair
sudo apt-get update
sudo apt-get install -y boot-repair
```

同样是图形化界面，但是小坑不少

1.  运行前询问是否是移动硬盘，当然不是。
2.  高级设置 第二栏，选择安装对应的位置，一定选择你要要拷贝的到磁盘 sda1
3.  还有老提示你让你安装 EFI 的引导，本来我的是legency 的引导，所以不用安装。

如果你在命令行中，成功看到grub更新完成，那么这就表示成功了！

重启，bios 设置一下磁盘启动顺序，然后应该就可以进入系统了。

## 参考文档

１．划好对应分区

> [https://www.zhihu.com/question/42115108](https://www.zhihu.com/question/42115108)

２．cp 磁盘文件

> [http://blog.csdn.net/lixiang201101/article/details/36531557](http://blog.csdn.net/lixiang201101/article/details/36531557)

3.Linux系统硬盘迁移

> [https://www.findhao.net/easycoding/2070](https://www.findhao.net/easycoding/2070)