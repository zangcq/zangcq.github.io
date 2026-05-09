---
title: "Tensorflow Dump HLO dot图"
date: 2020-05-04 12:13:46
categories: ["机器学习"]
permalink: "/2020/05/04/tensorflow-dump-hlo-dot%e5%9b%be/"
legacy: true
toc: true
classes: wide
---

1. DUMP HLO 和 NLO的dot图，便于查看XLA PASS间是否做了对应转换

```

    #nlo dump
    export TF_NLO_DUMP_GRAPH=true
    #xla hlo graph
    export TF_XLA_FLAGS="--xla_generate_hlo_graph=.* --xla_hlo_graph_path=./ "
```

  2. DUMP tensorflow graph 到 XLA 的pbtxt之间的转换图

```

    # 1. 打开log选项
    export TF_CPP_MIN_VLOG_LEVEL=4
    export TF_CPP_MIN_LOG_LEVEL=0
    # 2. 在/tmp 目录对应建立用户名 文件夹
    eg.
    mkdir /tmp/lingyao.zcq

    # 3. 运行bazel run example，可以在新建目录下看到对应pbtxt图
    source /home/lingyao.zcq/env.sh
    cd /home/lingyao.zcq/sinian_fpga_tensorflow
    bazel run tensorflow/cc/example:din_64

    ls /tmp/lingyao.zcq
    after_encapsulate_subgraphs.pbtxt
    before_encapsulate_subgraphs.pbtxt
    build_xla_launch_ops.pbtxt
    encapsulate_fdef_cluster_0.pbtxt
    encapsulate_fdef_graph_cluster_0.pbtxt
    functionalize_initial.pbtxt
    xla_compile_function_cluster_0__XlaCompiledKernel=true,_XlaNumConstantArgs=12,_XlaNumResourceArgs=0_.pbtxt
    xla_compile_graph_cluster_0__XlaCompiledKernel=true,_XlaNumConstantArgs=12,_XlaNumResourceArgs=0_.pbtxt
```
