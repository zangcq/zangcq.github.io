---
title: "Jetson TX1 or TX2 配置源 和 设置远程桌面Ubuntu xfce4"
date: 2017-08-19 16:43:17
categories: ["Jetson TX1-2"]
tags: ["Jetson", "tx1", "tx2"]
permalink: "/2017/08/19/jetson-tx1-or-tx2-%e9%85%8d%e7%bd%ae%e6%ba%90-%e5%92%8c-%e8%ae%be%e7%bd%ae%e8%bf%9c%e7%a8%8b%e6%a1%8c%e9%9d%a2ubuntu-xfce4/"
legacy: true
toc: true
classes: wide
---

为了使用Ubuntu 的远程桌面，做了很多尝试，只有使用 xfce4 结合 vnc 可以使用

## （一）配置源
```

     motify /etc/apt/source.list and update

```

#### 1\. 修改 /etc/apt/source.list

`sudo vi /etc/apt/source.list`
press i to go into the Insert mode , copy the flow detail
```

    USTC的源

```
```

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
```

     sudo apt-get install xrdp vnc4server xubuntu-desktop

```

### 2.重启服务
```

     echo "xfce4-session" >~/.xsession
     sudo service xrdp restart

```

### 2.5 远程连接

我用的是ubuntu gnome ，，直接在Remmina 新建一个连接即可

### 3.xfce4配置

默认配置即可

主要配置两个 panel ，根据自己的喜好配置两个 panel 。

### 4.效果图

*(Legacy image unavailable; original hosted on CSDN.)*
