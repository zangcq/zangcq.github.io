---
title: 可视化Caffe weight（非Net方法）
tags: []
id: '939'
categories:
  - - 机器学习
comments: false
date: 2019-08-29 11:25:10
---

#### 1\. 使用可视化工具 netron，打开caffemodel

![](http://www.zangcq.com/wp-content/uploads/2019/08/image.png)

#### 2\. np.load() 读取a.py

```
# !/usr/bin/python

import numpy as np

weight = np.load('a.npy')

print weight
```