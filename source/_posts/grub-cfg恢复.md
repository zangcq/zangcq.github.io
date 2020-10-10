---
title: grub.cfg恢复
tags:
  - Linux
  - Shell
id: '155'
categories:
  - - tools
    - 系统管理维护
date: 2017-07-06 21:02:49
---

## 记 一次手残 将grub 启动项弄没了的尴尬经历\*\*

这是一个悲催的故事，作者新装的debian8.0，缘于资深博客虾师弟find的影响，本机是120Gssd+500G机械；本来机械硬盘里有个ubuntu16.04，然后又装了个win7，我想利用强大的grub来引导一下，多次折腾之后没有成功，结果一时手残，把两个在/boot下重要文件给 rm 掉了 ，![boot目录下的文件](http://img.blog.csdn.net/20160915224117952) vmlinuz-\*\*和initrd.img~这两文件，相当重要，千万不要跟我一样。 下面我说一下这个过程，和遇到的问题。

$$1.发现不能进入debian的时候，我就开始想怎么解决这个问题了，谷歌一下，搜索到的都是利用liveCD，重新安装grub。搜到一篇文章，不过文不对题\[这篇文章主要解决的是win7+ubuntu双系统，更新grub\](https://www.hongweipeng.com/index.php/archives/153/)

2.此法不通，另寻它法。我又折腾了一会儿，发现能进grub命令行，我想通过grub命令能不能解决这个问题，又展开搜索了。终于发现了问题所在，\[How to Rescue a Non-booting GRUB 2 on Linux\](https://www.linux.com/learn/how-rescue-non-booting-grub-2-linux),原来我的两个文件被我rm掉了啊，难怪我无法修复呢。 3.发现问题之后，我准备着手解决，但是更悲催的是，grub.cfg里的代码又被我无情的delete掉了，苍了个天。幸好有位好同志，将cfg文件的代码贴了出来，终于照着葫芦画瓢给写上了。\[grub.cfg源码\](http://blog.chinaunix.net/uid-7374279-id-5640169.html)。 把grub.cfg的几段代码贴一下。 第一个，引导debian8.0的代码。$$

```c

menuentry 'Debian GNU/Linux' --class debian --class gnu-linux --class gnu --class os $menuentry_id_option 'gnulinux-simple-8f9a2097-a3bb-4265-9896-3fb64411f2f6' {
load_video
insmod gzio
if [ x$grub_platform = xxen ]; then insmod xzio; insmod lzopio; fi
insmod part_msdos
insmod ext2
set root='hd1,msdos1'#debian8.0安装盘所在位置
if [ x$feature_platform_search_hint = xy ]; then
  search --no-floppy --fs-uuid --set=root --hint-bios=hd1,msdos1 --hint-efi=hd1,msdos1 --hint-baremetal=ahci1,msdos1  4c6cb16d-8aa6-4833-8d70-7ab013f1f386#/boot的磁盘名
else
  search --no-floppy --fs-uuid --set=root 4c6cb16d-8aa6-4833-8d70-7ab013f1f386
fi
echo'载入 Linux 3.16.0-4-amd64 ...'
linux/vmlinuz-3.16.0-4-amd64 root=UUID=8f9a2097-a3bb-4265-9896-3fb64411f2f6 ro initrd=/install/initrd.gz quiet#8f...是 / 的磁盘名
#vmlinuz是boot下文件
echo'载入初始化内存盘...'
initrd/initrd.img-3.16.0-4-amd64#initrd镜像
}
```

知道各个位置所在，就可以直接改写代码了。

$$跟debian类似，这是ubuntu16.04的代码$$

```c

menuentry 'Ubuntu 16.04' --class debian --class gnu-linux --class gnu --class os $menuentry_id_option 'gnulinux-simple-61438d84-4200-47f5-8f8f-12a537bd1ac7' {
load_video
insmod gzio
if [ x$grub_platform = xxen ]; then insmod xzio; insmod lzopio; fi
insmod part_msdos
insmod ext2
set root='hd0,msdos5'
if [ x$feature_platform_search_hint = xy ]; then
  search --no-floppy --fs-uuid --set=root --hint-bios=hd0,msdos5 --hint-efi=hd0,msdos5 --hint-baremetal=ahci0,msdos5  cc13b962-d94d-4d32-ae46-26c2ddeb4e9c
else
  search --no-floppy --fs-uuid --set=root cc13b962-d94d-4d32-ae46-26c2ddeb4e9c
fi
echo'载入 Linux 3.16.0-4-amd64 ...'
linux/vmlinuz-4.4.0-36-generic root=UUID=61438d84-4200-47f5-8f8f-12a537bd1ac7 ro initrd=/install/initrd.gz quiet
echo'载入初始化内存盘...'
initrd/initrd.img-4.4.0-36-generic
}
```

$$win7代码如下$$

```c

# This entry automatically added by the Debian installer for a non-linux OS
# on /dev/sda1
menuentry "Windows 7 (loader) (on /dev/sda1)" --class windows --class os {
insmod part_msdos
insmod ntfs
set root='(/dev/sda,msdos1)'#c盘所在
if [ x$feature_platform_search_hint = xy ]; then
  search --no-floppy --fs-uuid --set=root --hint-bios=hd0,msdos1 --hint-efi=hd0,msdos1 --hint-baremetal=ahci0,msdos1  54E405AEE4059400
else
search --no-floppy --fs-uuid --set=root 54E405AEE4059400#c盘盘符
fi
chainloader +1
}
```

参考文献 \[1\] [https://www.hongweipeng.com/index.php/archives/153/](https://www.hongweipeng.com/index.php/archives/153/) \[2\] [https://www.linux.com/learn/how-rescue-non-booting-grub-2-linux](https://www.linux.com/learn/how-rescue-non-booting-grub-2-linux) \[3\] [http://blog.chinaunix.net/uid-7374279-id-5640169.html](http://blog.chinaunix.net/uid-7374279-id-5640169.html)