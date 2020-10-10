---
title: Caffe 中两种读取图片的方式 （python）
tags: []
id: '937'
categories:
  - - programming
    - Python
  - - 机器学习
comments: false
date: 2019-08-29 11:15:11
---

读取一张jpg图片（压缩格式）

##### 图表对比

类别

cv2.imread()

caffe.io.load\_image()

所在库

import cv2

import caffe

数据类型

0~255 \[unsigned char\]

0~1 \[float\]

Channel排列

BGR

RGB

三维数组方向

HWC

HWC

##### Python Code

```
from __future__ import print_function
import argparse
import numpy as np
from func import *
import caffe
import struct
import cv2

def get_arg():
  parser = argparse.ArgumentParser(description='inference automaticlly')
  parser.add_argument('model', type=str, help='model prototxt for inference' )
  parser.add_argument('weight', type=str, help='model weights(caffemodel) for inference')
  # parser.add_argument('image', type=str, help='image for inference')
  args = parser.parse_args()
  return args

if __name__ == '__main__':
  args = get_arg()
  # caffe.set_device(0)
  # caffe.set_mode_gpu()
  # net =  caffe.Net(args.model, args.weight, caffe.INT8)
  net =  caffe.Net(args.model, args.weight, caffe.TEST)

  # create transformer for the input called 'data'
  transformer = caffe.io.Transformer({'data':net.blobs['data'].data.shape})

  # load image by caffe
  image = caffe.io.load_image('/home/caffe/autoquan/123_608x608.jpg')

  # HWC -> CHW
  # transformer.set_transpose('data', (2,0,1))
  # transformer.set_mean('data', mu)
  transformer.set_raw_scale('data', 255)
  # RGB -> BGR
  # transformer.set_channel_swap('data', (2,1,0))

  transformed_image = transformer.preprocess('data', image)
  print ("transformed_image = ",transformed_image)

  # load image by opencv2
  image1 = cv2.imread('/home/caffe/autoquan/123_608x608.jpg')
  #  BGR -> RGB
  image1 = cv2.cvtColor(image1, cv2.COLOR_BGR2RGB)

  is_equal = np.all(transformed_image == image1)
  print("cvt 2 RGB = ", image1)

  print (is_equal)
```