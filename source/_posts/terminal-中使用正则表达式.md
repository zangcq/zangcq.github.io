---
title: terminal 中使用正则表达式
tags: []
id: '854'
categories:
  - - 工欲善其事必先利其器
date: 2019-06-17 17:40:19
---

例如批量创建文件夹 tile10 到 tile20

mkdir tile\_{10..19}

或者删除文件夹

rm tile\_{10..19} -rf