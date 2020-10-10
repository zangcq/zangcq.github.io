---
title: Jetson TX1 or TX2 配置源 和 设置远程桌面Ubuntu xfce4
tags:
  - Jetson
  - tx1
  - tx2
id: '363'
categories:
  - - gpu-computing
    - Jetson TX1-2
date: 2017-08-19 16:43:17
---

为了使用Ubuntu 的远程桌面，做了很多尝试，只有使用 xfce4 结合 vnc 可以使用

## （一）配置源

```c++

 motify /etc/apt/source.list and update
```

#### 1\. 修改 /etc/apt/source.list

`sudo vi /etc/apt/source.list`  
press i to go into the Insert mode , copy the flow detail

```c++

USTC的源
```

```c++

deb http://mirrors.ustc.edu.cn/ubuntu-ports/  xenial main restricted universe multiverse

deb http://mirrors.ustc.edu.cn/ubuntu-ports/  xenial-updates main restricted universe multiverse

deb http://mirrors.ustc.edu.cn/ubuntu-ports/  xenial-security main restricted universe multiverse

deb-src http://mirrors.ustc.edu.cn/ubuntu-ports/  xenial main restricted universe multiverse

deb-src http://mirrors.ustc.edu.cn/ubuntu-ports/  xenial-updates main restricted universe multiverse

deb-src http://mirrors.ustc.edu.cn/ubuntu-ports/  xenial-security main restricted universe multiverse
```

#### 2\. 更新 then update source

`sudo apt-get update`

## （二） 安装 并设置远程桌面

### 1.开始安装

```c++

 sudo apt-get install xrdp vnc4server xubuntu-desktop
```

### 2.重启服务

```c#

 echo "xfce4-session" >~/.xsession
 sudo service xrdp restart
```

### 2.5 远程连接

我用的是ubuntu gnome ，，直接在Remmina 新建一个连接即可

### 3.xfce4配置

默认配置即可

主要配置两个 panel ，根据自己的喜好配置两个 panel 。

### 4.效果图

![这里写图片描述](http://img.blog.csdn.net/20170819162516186?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvZGFyazU2Njk=/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)