---
title: 深度学习概念理解 ROI
tags: []
id: '785'
categories:
  - - 机器学习
date: 2019-05-07 21:10:58
---

#### ROI Pooling

##### 概念

*   region of interest
*   特征图上的框
*   在Fast RCNN中， RoI是指Selective Search完成后得到的“候选框”在特征图上的映射
*   在Faster RCNN中，候选框是经过RPN产生的，然后再把各个“候选框”映射到特征图上，得到RoIs。

##### input

输入有两部分组成：

*   **特征图**：指的是图1中所示的特征图，在Fast RCNN中，它位于RoI Pooling之前，在Faster RCNN中，它是与RPN共享那个特征图，通常我们常常称之为“share\_conv”；
*   **rois**：在Fast RCNN中，指的是Selective Search的输出；在Faster RCNN中指的是RPN的输出，一堆矩形候选框框，形状为1x5x1x1（4个坐标+索引index），其中**值得注意**的是：坐标的参考系不是针对feature map这张图的，而是**针对原图**的（神经网络最开始的输入）

##### Pooling 池化

![Region of interest pooling example (pooling sections)](https://deepsense.ai/wp-content/uploads/2017/02/3.jpg)

要做2x2的最大池化，原Roi是5x7的,那么无法均分:

h方向： 5/2 = 2 (2,3)

w方向：7/2 = 3 (3,4)

##### output

![Region of interest pooling example (output)](https://deepsense.ai/wp-content/uploads/2017/02/output.jpg)

##### Reference

> [https://blog.csdn.net/lanran2/article/details/60143861](https://blog.csdn.net/lanran2/article/details/60143861)
> 
> [https://github.com/deepsense-ai/roi-pooling](https://github.com/deepsense-ai/roi-pooling)
> 
> [https://deepsense.ai/region-of-interest-pooling-explained/](https://deepsense.ai/region-of-interest-pooling-explained/)

#### ROI Align

##### 线性插值

假设我们已知坐标 (_x_0, _y_0) 与 (_x_1, _y_1)，要得到 \[_x_0, _x_1\] 区间内某一位置 _x_ 在直线上的值。根据图中所示，我们得到

$\\frac{y - y\_0}{x - x\_0} = \\frac{y\_1 - y\_0}{x\_1 - x\_0}. \\,!$

由于 _x_ 值已知，所以可以从公式得到 y 的值

$y = y\_0 + (x-x\_0)\\frac{y\_1 - y\_0}{x\_1-x\_0} = y\_0 + \\frac{(x-x\_0) y\_1 - (x-x\_0) y\_0}{x\_1-x\_0}$

已知 _y_ 求 _x_ 的过程与以上过程相同，只是 _x_ 与 _y_ 要进行交换。

![Linear interpolation.png](https://upload.wikimedia.org/wikipedia/commons/6/68/Linear_interpolation.png)

##### 双线性差值

![img](https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Bilinear_interpolation.png/220px-Bilinear_interpolation.png)

即做三次线性插值 R1，R2，P

> [https://zh.wikipedia.org/wiki/%E5%8F%8C%E7%BA%BF%E6%80%A7%E6%8F%92%E5%80%BC](https://zh.wikipedia.org/wiki/双线性插值)

##### 具体流程

如下图所示，虚线部分表示feature map，实线表示ROI，这里将ROI切分成2x2的单元格。

*   如果采样点数是4，那我们首先将每个单元格子均分成四个小方格（如红色线所示），每个小方格中心就是采样点。
*   这些采样点的坐标通常是浮点数，所以需要对采样点像素进行**双线性插值**（如四个箭头所示），就可以得到该像素点的值了。
*   然后对每个单元格内的四个采样点进行maxpooling，就可以得到最终的ROIAlign的结果。

![](http://www.zangcq.com/wp-content/uploads/2019/05/roi-align.png)