---
title: grub修改默认顺序
tags:
  - Linux
  - Shell
id: '152'
categories:
  - - tools
    - 系统管理维护
date: 2017-07-06 21:01:48
---

## 修改grub引导顺序

修改`/etc/default/grub`文件

```powershell

sudo gedit /etc/default/grub
```

内容

```shell

GRUB_DEFAULT=0
#GRUB_HIDDEN_TIMEOUT=0
GRUB_HIDDEN_TIMEOUT_QUIET=true
GRUB_TIMEOUT=10
GRUB_DISTRIBUTOR=`lsb_release -i -s 2> /dev/null  echo Debian`
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"
GRUB_CMDLINE_LINUX="locale=zh_CN"

```

开机时显示default顺序

```shell

Ubuntu
Advanced options for Ubuntu
Memory test (memtest86+)
Memory test (memtest86+, serial console 115200)
Windows 8 (loader) (on /dev/sda1)
```

windows排第4（ 注意，顺序是从0开始计的），所以，把GRUB\_DEFAULT的值修改为4，然后别忘了运行命令：

sudo update-grub

那么结果就可以让windows 作为默认启动了