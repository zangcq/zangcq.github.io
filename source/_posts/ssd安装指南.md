---
title: SSD安装指南
tags:
  - Deep learning
  - SSD-Caffe
id: '120'
categories:
  - - DAC-SDC
date: 2017-12-22 18:27:50
---

SSD（Single Shot MultiBox Detector）算是一个比较不错的目标检测算法，主攻方向是速度，当然精度也比Yolo提高了一些，最近在ubuntu16.04下实现了代码运行，此博文主要内容来自原作者的github，加上了一些个人理解，欢迎探讨。 ****PS：SSD代码和模型常常在更新，我给的链接可能不是最新版，如运行出错请参看官方github。**** 准备工作：linux+cuda+caffe是标配，我就不详述了，推荐博客： 下面正式开始：

### **1.** ****获取源码****

### ****git clone https://github.com/weiliu89/caffe.git**** 

### ****cd caffe**** 

### ****git checkout ssd**** 

说明：SSD采用的是在caffe文件夹中内嵌例程的方式，作者改动了原版caffe，所以你需要把原来的caffe文件夹移除，git命令会新建一个带有SSD程序的caffe文件夹，当然，这个新的caffe要重新编译一次。

### **2.** ****编译caffe****

### ****cd /home/mx/caffe****

### ****cp Makefile.config.example Makefile.config** ** ****运行时报错不断，事后总结，需要修改配置文件，用gedit或者vim打开配置文件进行修改：****

1）Makefile.config文件中 将USE\_CUDNN :=1取消注释 2）Makefile.config文件中 INCLUDE\_DIRS := $(PYTHON\_INCLUDE) /usr/local/include后面打上一个空格， 然后添加/usr/include/hdf5/serial， 如果没有这一句会报一个找不到hdf5.h的错误 3）makefile文件中 替换NVCCFLAGS += -ccbin=$(CXX) -Xcompiler -fPIC $(COMMON\_FLAGS) 为NVCCFLAGS += -D\_FORCE\_INLINES -ccbin=$(CXX) -Xcompiler -fPIC $(COMMON\_FLAGS) 保存退出。 继续输入命令 make -j8 #8线程 make py make test -j8 make runtest -j8 #貌似不是必须的，跑一遍用了10多分钟

### ****3.训练模型****

节省时间的做法是，直接下载原作者最终弄好的模型： [http://www.cs.unc.edu/~wliu/projects/SSD/models\_VGGNet\_VOC0712\_SSD\_300x300.tar.gz](http://www.cs.unc.edu/~wliu/projects/SSD/models_VGGNet_VOC0712_SSD_300x300.tar.gz) 解压后将voc0712文件夹放入/home/mx/caffe/models/VGGNet/之下 OR：条件较好的同学可以下载图片数据和预训练模型，进行finetuning，得到最终可用的模型，步骤如下： 1）下载预训练模型 [https://gist.github.com/weiliu89/2ed6e13bfd5b57cf81d6](https://gist.github.com/weiliu89/2ed6e13bfd5b57cf81d6) 将其放入新建的文件夹/home/mx/caffe/models/VGGNet/

*   下载voc2007和voc2012数据集

cd /home/mx/data wget http://host.robots.ox.ac.uk/pascal/VOC/voc2012/VOCtrainval\_11-May-2012.tar wget http://host.robots.ox.ac.uk/pascal/VOC/voc2007/VOCtrainval\_06-Nov-2007.tar wget http://host.robots.ox.ac.uk/pascal/VOC/voc2007/VOCtest\_06-Nov-2007.tar 如果终端下载太慢，那就按照地址手动下载文件，依然放入文件夹/home/mx/data/ 解压文件，按照顺序来 cd /home/mx/data tar -xvf VOCtrainval\_11-May-2012.tar tar -xvf VOCtrainval\_06-Nov-2007.tar tar -xvf VOCtest\_06-Nov-2007.tar

*   将图片转化为LMDB文件，用于训练

cd /home/mx/caffe ./data/VOC0712/create\_list.sh ./data/VOC0712/create\_data.sh 这里用的脚本实现批处理，可能会出现错误：no module named caffe或者no module named caffe-proto，那是caffe的Python环境变量未配置好，解决方法： echo "export PYTHONPATH=/home/username/caffe/python:$PYTHONPATH" >> ~/.profile source ~/.profile echo $PYTHONPATH #检查环境变量的值 设好环境变量后，重新运行命令就不会出错了