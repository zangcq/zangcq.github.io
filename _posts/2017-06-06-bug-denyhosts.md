---
title: "BUG 在安装 denyhosts 的时候无法启动服务"
date: 2017-06-06 14:42:55
categories: ["系统管理维护"]
permalink: "/2017/06/06/bug-%e5%9c%a8%e5%ae%89%e8%a3%85-denyhosts-%e7%9a%84%e6%97%b6%e5%80%99%e6%97%a0%e6%b3%95%e5%90%af%e5%8a%a8%e6%9c%8d%e5%8a%a1/"
legacy: true
toc: true
classes: wide
---

这个bug已经被提交 > https://bugzilla.redhat.com/show_bug.cgi?id=1014473 如题目所说，在安装完成`denyhosts` 的时候，想启动此服务，出现了 [Errno 2] No such file or directory: '/var/log/secure' Error deleting DenyHosts lock file: /var/lock/subsys/denyhosts 这两个错误。 通过尝试这个ubuntu社区的解决方法 > https://ubuntuforums.org/archive/index.php/t-254149.html 对`denyhosts.cfg` 进行修改 `vi denyhosts.cfg` 将以下两项修改即可 `SECURE_LOG = /var/log/auth.log` `LOCK_FILE = /var/run/denyhosts.pid`
