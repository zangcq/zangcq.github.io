---
title: yolo训练日志
tags: []
id: '507'
categories:
  - - 机器学习
date: 2017-12-21 21:22:04
---

## yolo训练日志

通过两天的训练,得到训练后的权值,效果有喜有忧.

1.  数据量的大小对训练的影响.
    
    第一次训练的图片约为6000张
    
    第一次训练的图片约为94000张
    
    迭代次数为120000次
    
    准确度是否与数据集大小成正相关?
    
    但是效果却不明显.
    
2.  参数设置对训练的影响
    
    net
    
    ```shell
    
    # batch：每次迭代要进行训练的图片数量
    # subdivisions：源码中的图片数量int imgs = net.batch * net.subdivisions * ngpus，按subdivisions大小分批进行训练 
    batch=64      
    subdivisions=8
    
    # width：输入图片宽度， height：输入图片高度，channels ：输入图片通道数
    width=416
    height=416
    channels=3
    
    momentum=0.9
    decay=0.0005
    
    # 对于每次迭代训练，YOLOv2会基于角度(angle)，饱和度(saturation)，曝光(exposure)，色调(hue)产生新的训练图片
    # angle：图片角度变化，单位为度，假如angle=5，就是生成新图片的时候随机旋转-5~5度 
    angle=0
    # saturation & exposure: 饱和度与曝光变化大小，tiny-yolo-voc.cfg中1到1.5倍，以及1/1.5~1倍 
    saturation = 1.5
    exposure = 1.5
    # hue：色调变化范围，tiny-yolo-voc.cfg中-0.1~0.1 
    hue=.1
    
    # 学习率
    learning_rate=0.001
    # max_batches：最大迭代次数 
    max_batches = 120000
    
    # 按照steps策略调整学习率，还有EXP，CONSTANT，POLY等
    policy=steps
    # 根据batch_num调整学习率
    steps= -1,100,80000,100000
    # 学习率变化的比例，累计相乘
    scales=.1,10,.1,.1
    ```
    
    convolution
    
    ```shell
    
    batch_normalize=1
    
    #卷积核的个数  
    filters=512
    
    size=3
    stride=1
    pad=1
    
    #leaky激活函数，大于0的为x,小于0的为0  
    activation=leaky 
    ```
    
    max pool
    
    ```shell
    
    size=2
    stride=1
    ```
    
    region
    
    ```shell
    
    # anchors：预测框的初始宽高，第一个是w，第二个是h，总数量是num*2，
    # YOLOv2作者说anchors是使用K-MEANS获得，其实就是计算出哪种类型的框比较多，可以增加收敛速度，
    # 如果不设置anchors，默认是0.5，还有就是anchors读入参数中名字是biases 
    anchors = 0.738768,0.874946,  2.42204,2.65704,  4.30971,7.04493,  10.246,4.59428,  12.6868,11.8741
    
    #在YOLOv2中anchors的维度是通过对GT聚类得到的，所给出的5个尺度肯定是适用于VOC2007 2012数据集的，如果借鉴的网络训练自己的数据，就需要更改这个anchor的尺度，anchor的个数当然是越多越好，兼顾效率和精度，作者选了5个，对于小目标这个没有直接的关系，希望能帮到你。
    
    # bias_match：如果为1，计算best iou时，预测宽高强制与anchors一致 
    bias_match=1
    
    # classes：类别数量
    classes=98
    
    # coords： BoundingBox的tx,ty,tw,th，tx与ty是相对于左上角的gird，
    # 同时是当前grid的比例，tw与th是宽度与高度取对数 
    coords=4
    
    # num：每个grid预测的BoundingBox个数 
    num=5
    # softmax：如果为1，使用softmax作为激活函数
    softmax=1
    
    # jitter：利用数据抖动产生更多数据，YOLOv2中使用的是crop，filp，以及net层的angle，flip是随机的
    # crop就是jitter的参数，tiny-yolo-voc.cfg中jitter=.2，就是在0~0.2中进行crop
    # 通过抖动增加噪声，控制过拟合
    jitter=.2
    
    # rescore：决定使用哪种方式计算IOU的误差，为1时，使用当前best iou计算，为0时，使用1计算
    rescore=1
    
    # object_scale & noobject_scale & class_scale & coord_scale
    # YOLOv1论文中cost function的权重，哪一个更大，每一次更新权重的时候，对应方面的权重更新相对比重更大
    
    # 计算损失时，预测框中有物体的权重
    object_scale=5
    # 计算损失时，预测框中没有物体的权重
    noobject_scale=1
    # 计算类别损失时的权重
    class_scale=1
    # 计算损失时坐标偏差的权重
    coord_scale=1
    
    absolute=1
    
    # thresh：决定是否需要计算IOU误差的参数，大于thresh，IOU误差不会夹在cost function中 
    thresh = .6
    
    # random：如果为1每次迭代图片大小随机从320到608，步长为32，如果为0，每次训练大小与输入大小一致
    random=1
    ```
    
3.  输出结果分析
    
    ```shell
    
    Loaded: 0.000029 seconds
    Region Avg IOU: 0.776567, Class: 0.999925, Obj: 0.418946, No Obj: 0.000931, Avg Recall: 1.000000,  count: 8
    ...
    119999: 6.035534, 6.783708 avg, 0.000010 rate, 2.310784 seconds, 7679936 images
    ```
    
    *   Region Avg IOU： 这个是预测出的bbox和实际标注的bbox的交集 除以 他们的并集。显然，这个数值越大，说明预测的结果越好。
    *   Avg Recall： 这个表示平均召回率， 意思是 检测出物体的个数 除以 标注的所有物体个数。
    *   count： 标注的所有物体的个数。 如果 count = 6， recall = 0.66667， 就是表示一共有6个物体（可能包含不同类别，这个不管类别），然后我预测出来了4个，所以Recall 就是 4 除以 6 = 0.66667 。
    
    11999
    
    *   `11999`是~次数，`6.035534`是`train loss`，`6.783708 avg`是`avg train loss`，`0.000010 rate`是学习率， `2.310784 seconds`是 batch的处理时间， 最后是已经一共处理了多少张图片。
    *   重点关注 train loss 和avg train loss，这两个值应该是随着iteration增加而逐渐降低的。
    *   如果loss增大到几百那就是训练发散了，如果loss在一段时间不变，就需要降低learning rate或者改变batch来加强学习效果。
4.  如何处理呢
    
    *   找到 loss的极值点
    *   多训练个几万次
    *   迷茫中.....
    
    ### Reference
    
    > [http://blog.csdn.net/Fate\_fjh/article/details/70598510](http://blog.csdn.net/Fate_fjh/article/details/70598510)
    > 
    > [http://www.cnblogs.com/hansjorn/p/7491391.html](http://www.cnblogs.com/hansjorn/p/7491391.html)
    > 
    > 训练自己的数据集时 修改参数和代码
    > 
    > [http://blog.csdn.net/q6324266/article/details/54375452](http://blog.csdn.net/q6324266/article/details/54375452)
    > 
    > [http://blog.csdn.net/hysteric314/article/details/54097845](http://blog.csdn.net/hysteric314/article/details/54097845)