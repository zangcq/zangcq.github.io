---
title: git commit 前检查多余空格
tags: []
id: '834'
categories:
  - - 工欲善其事必先利其器
date: 2019-05-30 11:31:55
---

##### 正则表达式匹配

vim 查找 `/` 和`?`

*   行首空格

^\\+\\s\\+

*   行尾空格

\\s\\+$

*   替换%s

进入vim命令模式
:
#usage B 全局 替换 A
%s/A/B/g
# 
%s/\\s\\+$//g
#
%s/^\\+\\s\\+//g

##### 在vim命令行下 查看

:set list   
# tab键就会显示为 ^I ，$ 显示在行尾。
# 查看空格
/\\s

```
在.vimrc中添加以下代码后，重启vim即可实现按TAB产生4个空格：
set ts=4  (注：ts是tabstop的缩写，设TAB宽4个空格)
set expandtab

 

对于已保存的文件，可以使用下面的方法进行空格和TAB的替换：
TAB替换为空格：
:set ts=4
:set expandtab
:%retab!

 

空格替换为TAB：
:set ts=4
:set noexpandtab
:%retab!

 

加!是用于处理非空白字符之后的TAB，即所有的TAB，若不加!，则只处理行首的TAB
```