---
title: macOS 串口调试汇总
tags: []
id: '792'
categories:
  - - 工欲善其事必先利其器
date: 2019-05-12 15:09:12
---

#### 连线

1.  将线的网口头插入板卡（alibaba edge）左一口 IOIOI
2.  将usb口插入mac

#### 下载驱动

*   打开Mac硬件信息查看USB详情

![](http://www.zangcq.com/wp-content/uploads/2019/05/image-20190509195046761.png)

*   搜索对应厂商，对应产品id[https://plugable.com/drivers/prolific/](https://plugable.com/drivers/prolific/)下载对应驱动
*   安装即可，注意偏好设置为 允许

> [https://www.jianshu.com/p/e25009af3726](https://www.jianshu.com/p/e25009af3726)
> 
> [https://software.intel.com/en-us/setting-up-serial-terminal-on-system-with-mac-os-x](https://software.intel.com/en-us/setting-up-serial-terminal-on-system-with-mac-os-x)

#### 连接串口设备

*   Screen 命令 
    *   sudo screen -L /dev/cu.usbserial 115200 -L
    *   可以连接，但是有乱码
    *   [https://software.intel.com/en-us/setting-up-serial-terminal-on-system-with-mac-os-x](https://software.intel.com/en-us/setting-up-serial-terminal-on-system-with-mac-os-x)
    *   screen 用法[https://www.cnblogs.com/mchina/archive/2013/01/30/2880680.html](https://www.cnblogs.com/mchina/archive/2013/01/30/2880680.html)
*   minicom
    *   install
    *   `brew install minicom`
    *   setting
    *   `sudo minicom -s`
        1.  `Serial port setup`按a键，选择串口设置，直接输入 `/dev/cu.usbserial`敲两下回车键，保存设置
        2.  选择 Exit 即可进入串口终端
        3.  Mac 使用默认终端的话，要map一下键位option -> meta鼠标在Terminal窗口左上方悬停，等待出现顶层菜单，选择：Terminal／Preferences／Keyboard，勾选“Use Option As Meta Key

*   Putty install
    *   [https://onvinetech.wordpress.com/2016/01/26/49/](https://onvinetech.wordpress.com/2016/01/26/49/)装好了，但是显示不了，待解决
*   Apple Store (免费能用版) Serial tools直接安装
    *   设置一下

![](http://www.zangcq.com/wp-content/uploads/2019/05/image.png)