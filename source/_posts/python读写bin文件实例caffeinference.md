---
title: Python读写bin文件实例CaffeInference
tags:
  - Caffe
  - Python
  - 机器学习
id: '921'
categories:
  - - programming
    - Python
  - - 机器学习
date: 2019-08-16 10:47:23
---

#### Reference

> https://docs.python.org/2/library/struct.html#struct-examples

#### Overview

有时需要将data暂时存储到二进制文件中以便使用，大概需要注意两个问题。

*   数据类型 char 1字节 int 4字节 float 4字节 double 8字节
*   字节按照大端或者小端顺序 eg. 0x12345678 大端-高位字节低地址 0x00 12 0x01 34 0x02 56 0x03 78 小端-高位字节高地址 0x00 78 0x01 56 0x02 34 0x03 12

> 阮一峰理解
> 
> http://www.ruanyifeng.com/blog/2016/11/byte-order.html
> 
> 国外老铁
> 
> https://blog.erratasec.com/2016/11/how-to-teach-endian.html#.XVTANZMzb\_8

大概注意到这两个问题就可以了。

python pack这个函数就是来进行对数据进行二进制转化的，其对应的unpack函数是他的逆操作

#### 对应语法

##### 字节序

Character

Byte order

Size

Alignment

@

native

native

native

\=

native

standard

none

<

little-endian

standard

none

\>

big-endian

standard

none

!

network (= big-endian)

standard

none

##### 常用数据类型

Format

C Type

Python type

Standard size

Notes

x

pad byte

no value

c

char

string of length 1

1

b

signed char

integer

1

\-3

B

unsigned char

integer

1

\-3

i

int

integer

4

\-3

I

unsigned int

integer

4

\-3

l

long

integer

4

\-3

L

unsigned long

integer

4

\-3

#### 举例说明

##### 写文件pack()

```
def write_file0(result, name):
  file_ = open(name, 'wb')
  for n in result:
    for h in n:
      for w in h:
        # byte=struct.pack('<B',w)
        # B for unsigned char
        # b for signed char
        byte=struct.pack('<b',w)
        file_.write(byte)
  file_.close()

def write_file1(result, name):
  file_ = open(name, 'wb')
  for n in result:
    for h in n:
      for w in h:
        #for c in w:
        # i for int
        # f for float
        # < for little edition
        byte=struct.pack('<f',w)
        file_.write(byte)
  file_.close()
```

读文件unpack()

*   读char

```
import struct
import sys
#import os
#from os.path import getsize
print ("usage: ")
print ("python read-data.py data.bin ")
print ("data file name:"+sys.argv[1])

datafile=open(sys.argv[1], 'rb')
total=0
while True:
      num1 = datafile.read(1)
      if(len(num1) == 0):
          break;
      num1 = struct.unpack('b', num1)[0]
      if(total < 32):
        print (num1)
      total = total+1
datafile.close()
```

*   读float类型

```
  import struct
  import sys
  #import os
  #from os.path import getsize
  print ("usage: ")
  print ("python readbin.py golden.bin ")
  print ("data file name:"+sys.argv[1])

  datafile=open(sys.argv[1], 'rb')
  total=0
  while True:
        num1 = datafile.read(4)
        if(len(num1) == 0):
            break;
        num1 = struct.unpack('f', num1)[0]
        if(total < 32):
          print (num1)
        total = total+1
  datafile.close()
```

##### 具体事例 Caffe-inference Demo

```
#!/usr/bin/python
from __future__ import print_function
import argparse
import numpy as np
from func import *
import caffe
import struct

def write_file0(result, name):
  file_ = open(name, 'wb')
  for n in result:
    for h in n:
      for w in h:
        # byte=struct.pack('<B',w)
        # B for unsigned char
        # b for signed char
        byte=struct.pack('<b',w)
        file_.write(byte)
  file_.close()

def write_file1(result, name):
  file_ = open(name, 'wb')
  for n in result:
    for h in n:
      for w in h:
        #for c in w:
        # i for int
        # f for float
        # < for little edition
        byte=struct.pack('<f',w)
        file_.write(byte)
  file_.close()

def get_arg():
  parser = argparse.ArgumentParser(description='inference automaticlly')
  parser.add_argument('model', type=str, help='model prototxt for inference' )
  parser.add_argument('weight', type=str, help='model weights(caffemodel) for inference')
  # parser.add_argument('image', type=str, help='image for inference')
  args = parser.parse_args()
  return args

if __name__ == '__main__':
  args = get_arg()
  caffe.set_device(0)
  caffe.set_mode_gpu()
  # net =  caffe.Net(args.model, args.weight, caffe.INT8)
  net =  caffe.Net(args.model, args.weight, caffe.TEST)
  # net =  caffe.Net(args.model, args.weight, caffe.QUAN)
  # create transformer for the input called 'data'
  transformer = caffe.io.Transformer({'data':net.blobs['data'].data.shape})

  # load the mean ImageNet image (as distributed with Caffe) for subtraction
  # mu = np.load('/home/caffe/python/caffe/imagenet/ilsvrc_2012_mean.npy')
  mean_array = np.array([[[128,128,128],[128,128,128]],[[128,128,128],[128,128,128]],[[128,128,128],[128,128,128]]])
  #mean_array.fill(128)
  print (mean_array)
  np.save("mean.npy", mean_array)
  mu = np.load("mean.npy")
  mu = mu.mean(1).mean(1)  # average over pixels to obtain the mean (BGR) pixel values
  print (mu)
  print ('mean-subtracted values:', zip('BGR', mu))

  transformer.set_transpose('data', (2,0,1))
  transformer.set_mean('data', mu)
  transformer.set_raw_scale('data', 255)
  transformer.set_channel_swap('data', (2,1,0))

  # load image
  image = caffe.io.load_image('/home/caffe/autoquan/123_608x608.jpg')
  transformed_image = transformer.preprocess('data', image)
  print ("transformed_image = ",transformed_image)

  # set a random seed
  np.random.seed(1234)
  # random a int8 data for test
  random_data = np.random.randint(-127,127,size=(1,3,608,608))

  # copy image into net data
  net.blobs['data'].data[...] = transformed_image
  # net.blobs['data'].data[...] = random_data

  net.forward()

  for layer_name, blob in net.blobs.iteritems():
      # if(layer_name == 'layer17-yolo' or layer_name == 'layer24-yolo' or layer_name == 'data'):
      print ('chuanqiz : ' + layer_name + '\t' + str(blob.data.shape))
      layer_data = net.blobs[layer_name].data[0]
      # layer_data = layer_data.transpose((1,2,0))
      if(layer_name == 'data'):
        # do transpose
        # chw -> hwc
        layer_data = layer_data.transpose((1,2,0))
        # do padding
        # hwc -> hwc4
        pad_width = ((0,0),(0,0),(0,1))
        layer_data = np.pad(layer_data,pad_width,mode='constant',constant_values=(0,0))
        # print (layer_data)
        write_file0(layer_data, layer_name+".bin")
      else:
        # print (layer_data)
        layer_data = layer_data.transpose((1,2,0))
        write_file1(layer_data, layer_name+".bin")
```