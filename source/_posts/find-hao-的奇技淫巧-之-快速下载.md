---
title: Find Hao 的奇技淫巧　之　快速下载
tags:
  - Linux
id: '466'
categories:
  - - 日常扯淡
  - - tools
    - 系统管理维护
date: 2017-11-17 22:45:06
---

# Find Hao 的奇技淫巧　之　快速下载

工欲善其事必先利其器,下载速度很重!!!

### overview

*   百度网盘工具
*   proxychain 工具下载
*   如何获取cookie

### 百度网盘工具

### １.下载chrome 百度网盘插件

因为这个工具已经在扩展程序中下架了，所以我们只能从`github`上搞下来。

> [https://github.com/acgotaku/BaiduExporter](https://github.com/acgotaku/BaiduExporter)

```shell

git clone https://github.com/acgotaku/BaiduExporter.git
```

#### 2.将插件文件夹导入到chrome中

```c

chrome->更多工具->扩展程序->加载已解压的扩展程序
```

然后把如图中release文件夹导入即可. ![这里写图片描述](http://img.blog.csdn.net/20171118091725726?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvZGFyazU2Njk=/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)

效果如下 ![这里写图片描述](http://img.blog.csdn.net/20171118092019781?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvZGFyazU2Njk=/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast) 选择文本导出,有一条命令,可以直接复制到命令行即可.

#### 3.安装aria2

```c

sudo apt install aria2
```

#### 4.举例说明

```c

aria2c -c -s10 -k1M -x16 --enable-rpc=false -o "让我留在你身边.mp3" --header "User-Agent: netdisk;5.3.4.5;PC;PC-Windows;5.1.2600;WindowsBaiduYunGuanJia" --header "Referer: https://pan.baidu.com/disk/home" --header "Cookie: BDUSS=EowQ1VYZW5ac0lTdG9FODlycX4yeG0tZkNWdlRUMVgwckJab3NiUWhkSUhwd2xhSUFBQUFBJCQAAAAAAAAAAAEAAABK3ZUzwfW2~rSyAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAca4lkHGuJZR; pcsett=1511013148-7adfeac011662d8deff8d1d5a2fad989" "https://pcs.baidu.com/rest/2.0/pcs/file?method=download&app_id=250528&path=%2F%E8%AE%A9%E6%88%91%E7%95%99%E5%9C%A8%E4%BD%A0%E8%BA%AB%E8%BE%B9.mp3"
```

**重要参数说明**

*   aria2c 就是这个工具的控制台命令了
    
*   \-c 表示支持断点续传 continue的意思
    
*   \-s10 多线程下载
    
*   \-k 1M 表示块大小是1M
    
*   "让我留在你身边.mp3" 要保存的文件名字
    
*   "Cookie: " 就是下载的cookie了
    
*   "[https://pcs.baidu.com/rest/2.0/pcs/file?method=download&app\_id=250528&path=%2F%E8%AE%A9%E6%88%91%E7%95%99%E5%9C%A8%E4%BD%A0%E8%BA%AB%E8%BE%B9.mp3](https://pcs.baidu.com/rest/2.0/pcs/file?method=download&app_id=250528&path=%252F%E8%AE%A9%E6%88%91%E7%95%99%E5%9C%A8%E4%BD%A0%E8%BA%AB%E8%BE%B9.mp3)"
    
    这个就是文件地址了
    

### proxychain 工具

这是一个代理的下载器,为了墙外使用

#### 0.安装shadowsocks

`sudo pip install shadowsocks` 编辑好配置文件，保存到~/ss.json

```c

{
"server":"服务器 IP 地址", #VPS的IP地址
"server_port":8388, #监听的端口
"local_address": "127.0.0.1", #本地监听的IP地址，默认为主机
"local_port":1080, #本地监听的端口
"password":"mypassword", #服务密码
"timeout":300, #超时设置
"method":"aes-256-cfb" #加密方法，推荐 "aes-256-cfb"
}123456789
```

3.运行shadowsocks `/usr/local/bin/sslocal -c ~/ss.json`

#### 1\. 安装proxychans4

下载代码： `git clone https://github.com/rofl0r/proxychains-ng.git` 安装：

```c

./configure --prefix=/usr --sysconfdir=/etc
sudo make install
sudo make install-config
```

配置文件 `sudo gedit /etc/proxychains.conf`

在最后加上：`socks5 127.0.0.1 1080`

若有其他的协议如`socks4`的,删掉即可

1080 是端口号,就是你`ss.json`中的`local port.`

2.跨越式下载

就是再加一层

```c

proxychans aria2c -c -s10 -k1M -x16 
```

**至于如何番羽墙呢,详情请看findhao.net**

### 如何获取cookie呢

先假装下载这个文件,然后取消,按一下浏览器 F12 ,然后可以看到`network`栏中有你要下载的文件,点一下你下载的文件的 Header 中.可以看到了

如图所示 ![这里写图片描述](http://img.blog.csdn.net/20171118092122219?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvZGFyazU2Njk=/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)