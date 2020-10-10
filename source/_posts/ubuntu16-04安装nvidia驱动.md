---
title: Ubuntu16.04安装Nvidia驱动
tags: []
id: '168'
categories:
  - - 驱动安装
date: 2018-07-20 09:07:31
---

#### 0.下载Nvidia驱动

​ 官方下载地址：https://www.nvidia.cn/Download/index.aspx?lang=cn ​ 百度云下载地址：https://pan.baidu.com/s/1kesDnmiwAeBb6f9PDmJ0eg 密码：`j9cx`

#### 1.关闭secure boot

​ 重启计算机进入BIOS； ​ 选定Security选项卡->Secure Boot->回车选定Disable->F10：保存并退出。 _注：如果无法进入桌面，下面的操作可在tty模式下进行（`Ctrl+Alt+F1`）。_

#### 2.卸载原有Nvidia驱动

`sudo apt-get remove --purge nvidia*`

#### 3.禁用nouveau

这是Ubuntu初始使用的driver（可在 `系统设置->软件和更新->附加驱动` 处查看），所以在安装Nvidia驱动前应禁用之： `sudo gedit /etc/modprobe.d/blacklist.conf` ​ 在文末添加：

blacklist nouveau
options nouveau modeset=0

执行：`sudo update-initramfs -u` 重启：`reboot` 执行：`lsmod grep nouveau //如果没有输出，证明禁用成功`

#### 4.禁用X-Window服务

`sudo service lightdm stop` 进入tty模式：`Ctrl+Alt+F1`，使用用户名和密码登录

#### 5.安装Nvidia驱动

给驱动文件赋予执行权限：（在驱动文件所在目录ls，可查看是否有执行权限） `sudo chmod a+x NVIDIA-Linux-x86_64-384.59.run` 安装： `sudo ./NVIDIA-Linux-x86_64-384.59.run –no-opengl-files` 参数说明： `–no-opengl-files`表示不安装OpenGL文件。这个参数不可省略，以免循环登录。 安装过程中，会有一些引导选项，我都选的yes，亲测没有问题……如遇问题请指出。 重启：`reboot` 进入桌面后查看是否安装成功：`nvidia-smi`，出现显卡相关信息说明安装成功。

#### 6.关于Ubuntu18.04的一点小问题--循环登录

如果将系统升级成了Ubuntu18.04，重启后循环登录，解决方案如下：

sudo apt-get remove --purge nvidia-\* //卸载驱动
sudo apt-get install ubuntu-desktop   //重新安装桌面
sudo rm /etc/X11/xorg.conf 
echo 'nouveau'  sudo tee -a /etc/modules

重启之后就可以登录了，然后再按照上面的1-5步重新尝试安装驱动。

##### 感谢：

> [https://blog.csdn.net/CosmosHua/article/details/76644029](https://blog.csdn.net/CosmosHua/article/details/76644029) [https://blog.csdn.net/u012759136/article/details/53355781](https://blog.csdn.net/u012759136/article/details/53355781) [https://www.jianshu.com/p/34236a9c4a2f](https://www.jianshu.com/p/34236a9c4a2f)