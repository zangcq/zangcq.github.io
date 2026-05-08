---
title: "可视化Caffe weight（非Net方法）"
date: 2019-08-29 11:25:10
categories: ["机器学习"]
permalink: "/2019/08/29/%e5%8f%af%e8%a7%86%e5%8c%96caffe-weight%ef%bc%88%e9%9d%9enet%e6%96%b9%e6%b3%95%ef%bc%89/"
legacy: true
toc: true
classes: wide
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
