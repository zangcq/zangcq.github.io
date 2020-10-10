---
title: BUG 在安装 denyhosts 的时候无法启动服务
tags: []
id: '30'
categories:
  - - tools
    - 系统管理维护
date: 2017-06-06 14:42:55
---

这个bug已经被提交 > https://bugzilla.redhat.com/show\_bug.cgi?id=1014473 如题目所说，在安装完成`denyhosts` 的时候，想启动此服务，出现了 \[Errno 2\] No such file or directory: '/var/log/secure' Error deleting DenyHosts lock file: /var/lock/subsys/denyhosts 这两个错误。 通过尝试这个ubuntu社区的解决方法 > https://ubuntuforums.org/archive/index.php/t-254149.html 对`denyhosts.cfg` 进行修改 `vi denyhosts.cfg` 将以下两项修改即可 `SECURE_LOG = /var/log/auth.log` `LOCK_FILE = /var/run/denyhosts.pid`