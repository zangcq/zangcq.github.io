---
title: "Tensorflow 打包-pack"
date: 2020-05-04 12:25:44
categories: ["机器学习"]
permalink: "/2020/05/04/tensorflow-%e6%89%93%e5%8c%85-pack/"
legacy: true
toc: true
classes: wide
---

1. 用于din_64.py

#### Reference

> <https://zhuanlan.zhihu.com/p/37637446>
> 
> <https://www.tensorflow.org/api_docs/python/tf/stack>

#### Overview

理解pack与concat的区别：

  * tf.concat是沿某一维度拼接shape相同的张量，拼接生成的新张量维度不会增加。
  * 而tf.stack是在新的维度上拼接，拼接后维度加1

例如：
```
 
    import tensorflow as tf
    a = tf.constant([[1,2,3],[4,5,6]]) 
    b = tf.constant([[7,8,9],[10,11,12]])
    ab1 = tf.concat([a,b],axis=0)
    ab2 = tf.stack([a,b], axis=0)
    sess = tf.Session()
    print(sess.run(ab1)) 
    print(sess.run(ab2))
    print ab1
    print ab2
```

当 axis= 0时

![image-20191028151342313.png](https://intranetproxy.alipay.com/skylark/lark/0/2019/png/131289/1572353495716-65b2b8f7-68ea-4b50-acc5-a49eeb92fc9e.png)

###### 当 axis= 1时

![image-20191028153434573.png](https://intranetproxy.alipay.com/skylark/lark/0/2019/png/131289/1572353511287-701359b0-711e-490f-82c8-92e313fe54ec.png)
