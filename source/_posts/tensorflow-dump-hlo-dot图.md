---
title: Tensorflow Dump HLO dot图
tags: []
id: '1264'
categories:
  - - 机器学习
comments: false
date: 2020-05-04 12:13:46
---

1.  DUMP HLO 和 NLO的dot图，便于查看XLA PASS间是否做了对应转换

#nlo dump
export TF\_NLO\_DUMP\_GRAPH=true
#xla hlo graph
export TF\_XLA\_FLAGS="--xla\_generate\_hlo\_graph=.\* --xla\_hlo\_graph\_path=./ "

2.  DUMP tensorflow graph 到 XLA 的pbtxt之间的转换图

\# 1. 打开log选项
export TF\_CPP\_MIN\_VLOG\_LEVEL=4
export TF\_CPP\_MIN\_LOG\_LEVEL=0
# 2. 在/tmp 目录对应建立用户名 文件夹 
eg. 
mkdir /tmp/lingyao.zcq

# 3. 运行bazel run example，可以在新建目录下看到对应pbtxt图
source /home/lingyao.zcq/env.sh
cd /home/lingyao.zcq/sinian\_fpga\_tensorflow
bazel run tensorflow/cc/example:din\_64

ls /tmp/lingyao.zcq
after\_encapsulate\_subgraphs.pbtxt
before\_encapsulate\_subgraphs.pbtxt
build\_xla\_launch\_ops.pbtxt
encapsulate\_fdef\_cluster\_0.pbtxt
encapsulate\_fdef\_graph\_cluster\_0.pbtxt
functionalize\_initial.pbtxt
xla\_compile\_function\_cluster\_0\_\_XlaCompiledKernel=true,\_XlaNumConstantArgs=12,\_XlaNumResourceArgs=0\_.pbtxt
xla\_compile\_graph\_cluster\_0\_\_XlaCompiledKernel=true,\_XlaNumConstantArgs=12,\_XlaNumResourceArgs=0\_.pbtxt