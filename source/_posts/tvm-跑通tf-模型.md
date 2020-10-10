---
title: TVM 跑通TF 模型
tags: []
id: '1395'
categories:
  - - 机器学习
comments: false
date: 2020-08-07 14:44:34
---

# 0\. 参考文献

*   官方文档

> [https://tvm.apache.org/docs/tutorials/frontend/from\_tensorflow.html#sphx-glr-tutorials-frontend-from-tensorflow-py](https://tvm.apache.org/docs/tutorials/frontend/from_tensorflow.html#sphx-glr-tutorials-frontend-from-tensorflow-py)

*   AML 库

> [https://code.byted.org/lagrange/tvm\_tune](https://code.byted.org/lagrange/tvm_tune)

# 1\. Overview

*   前提条件，安装[tensorflow](https://www.tensorflow.org/install) ，版本1.15

*   下边是我 pip list 中相关与tvm和TensorFlow的各种依赖包列表，可以跑通。方便大家对照查看。

不支持在 Doc 外粘贴 block

*   根据官方文档的介绍，我用 processon 画一个流程图，来方便理解。

![img](https://bytedance.feishu.cn/space/api/box/stream/download/asynccode/?code=85c33df6a1f6b9464ed5ddae18aaa394_8f118824ce50c961_boxcnkWOIxuxBbOOTHckNIaUYLd_e38iOB16tbmPUtmnWAmQHNScEMIrsc1p)

*   名词解释

*   **pb**

*   Protobuf 类型的模型文件，一般用TensorFlow训练生成

*   **pbtxt**

*   文本文件，描述模型结构，人类可读，可以用一些可视化工具来查看

*   **np.array**

*   Numpy 的数组

*   **mod** (_tvm.IRModule_) – The module that optimizations will be performed on.

*   TVM 的中间表示，所有的优化都在这上边做

*   **params** (_dict of str to tvm.nd.NDArray_) – Dict of converted parameters stored in tvm.nd.NDArray format

*   存储参数的数据结构，在auto tune的时候，就调节它

*   **relay.build** 图优化就在这个阶段做

*   **graph\_json** (_str_) – The json string that can be accepted by graph runtime.

*   在运行时可以读取

*   **mod** (_tvm.Module_) – The module containing necessary libraries.

*   包含了运行所需要的库

*   **params** (_dict_) – The parameters of the final graph.

*   存贮图最终的参数

# 2\. 实际运行

运行一个 tvm\_tune的demo

```
 # https://code.byted.org/lagrange/tvm_tune
# 代码库下载
git clone git@code.byted.org:lagrange/tvm_tune.git
# 切换到对应分支
git checkout tf_pipeline
cd tvm_tune/tools
python tune_frozen_graph.py
```

## 在**CPU**上运行

1.  微调一下代码

```
diff --git a/tools/tune_frozen_graph.py b/tools/tune_frozen_graph.py
index 1ca63ed..ad5d252 100644
--- a/tools/tune_frozen_graph.py
+++ b/tools/tune_frozen_graph.py
@@ -23,11 +23,14 @@ from tvm.contrib.util import tempdir
 #### TUNING OPTION ####
-target = tvm.target.cuda("unknown", "-libs=cudnn,cublas")
+# target = tvm.target.cuda("unknown", "-libs=cudnn,cublas")
+target = tvm.target.cuda("unknown", "")
 print(target)
 network = 'bertmatch'
 log_file = "%s.log" % network
+print ("chuanqiz")
+print (log_file)
 tuning_option = {
   'log_filename': log_file,
@@ -224,15 +227,15 @@ if __name__ == "__main__":
   print(tf_res)
   export_path = "./tvm_export"
-   # mod, params = convert_tf_to_tvm(sess, input_names, input_shapes, output_names)
+   mod, params = convert_tf_to_tvm(sess, input_names, input_shapes, output_names)
   # print(mod["main"])
   #
-   # # tvm_res = run_tvm(mod, params, feed_dict, output_shapes)
-   # module = tune_and_evaluate(mod, tuning_option, params, export_path, skip_tune=True)
-   # tvm_res = run_tvm(module, None, feed_dict, output_shapes)
+   tvm_res = run_tvm(mod, params, feed_dict, output_shapes)
+   module = tune_and_evaluate(mod, tuning_option, params, export_path, skip_tune=True)
+   tvm_res = run_tvm(module, None, feed_dict, output_shapes)
   #
-   # print(tf_res, tvm_res)
-   # print(np.allclose(tf_res, tvm_res, rtol=1.e-3, atol=1.e-4))
+   print(tf_res, tvm_res)
+   print(np.allclose(tf_res, tvm_res, rtol=1.e-3, atol=1.e-4))
   # tvm tuned module export to tensorflow op
   export_tf_res = tvm_export_to_tensorflow(export_path, feed_dict, fetch_dict)
```

*   运行log留存，便于对比

## 在**GPU**上运行

1.  要把 +# target = tvm.target.cuda("unknown", "-libs=cudnn,cublas")这行代码打开

```
zangchuanqi@n22-145-158:~/workspace/tvm_tune/tools$ diff tune_frozen_graph_gpu.py tune_frozen_graph.py
26c26,27
< target = tvm.target.cuda("unknown", "-libs=cudnn,cublas")
---
> # target = tvm.target.cuda("unknown", "-libs=cudnn,cublas")
> target = tvm.target.cuda("unknown", "")
```

1.  重新编译 tvm ， 修改 config.cmake 文件

```
zangchuanqi@n22-145-158:~/workspace/tvm$ diff config.cmake build/config.cmake
173c173
< set(USE_CUDNN OFF)
---
> set(USE_CUDNN ON)
176c176
< set(USE_CUBLAS OFF)
---
> set(USE_CUBLAS ON)
227,229d226
```

*   log留存

## 需要安装的一些依赖

*   Import tensorflow as tf

```
pip install tensorflow 
```

*   ImportError: No module named PIL

```
pip install Pillow
```

*   Graph 读入部分，借助TF和pytorch的依赖

*   需要安装 tf 和 torch

*   出现问题，使用 包管理器安装时，由于网络原因无法安装，因此下载 whl，手动安装

*   或者添加代理，搞定网络问题

*   使用docker 镜像，安装对应环境

# 3\. 运行时出现的小问题

*   Warning 缺少llvm ，是否需要安装？

```
WARNING:autotvm:Cannot find config for target=llvm, workload=('dense_nopack.x86', ('TENSOR', (1, 2048), 'float32'), ('TENSOR', (1008, 2048), 'float32'), None, 'float32'). A fallback c    onfiguration is used, which may bring great performance regression.
```

*   block住了, python 语法问题？

```
Tensorflow protobuf imported to relay frontend.
Traceback (most recent call last):
 File "from_tensorflow.py", line 158, in <module>
  m = graph_runtime.GraphModule(lib["default"](ctx))
TypeError: tuple indices must be integers or slices, not str
```

*   TensorFlow中node不合法？

```
WARNING:tensorflow:From /data01/zangchuanqi/workspace/tvm/python/tvm/relay/testing/tf.py:153: The name tf.logging.fatal is deprecated. Please use tf.compat.v1.logging.fatal instead.
CRITICAL:tensorflow:Failed to locate: n01440764
Traceback (most recent call last):
 File "tf.py", line 146, in <module>
  run_inference_on_image(img_path)
 File "tf.py", line 136, in run_inference_on_image
  uid_lookup_path=label_path)
 File "/data01/zangchuanqi/workspace/tvm/python/tvm/relay/testing/tf.py", line 105, in __init__
  self.node_lookup = self.load(label_lookup_path, uid_lookup_path)
 File "/data01/zangchuanqi/workspace/tvm/python/tvm/relay/testing/tf.py", line 154, in load
  name = uid_to_human[val]
KeyError: 'n01440764'
(tvm.venv) zangchuanqi@n22-145-158:~/workspace/test$ cat  /data01/zangchuanqi/.tvm_test_data/data/imagenet_2012_challenge_label_map_proto.pbtxt  grep n01440764
 target_class_string: "n01440764"
(tvm.venv) zangchuanqi@n22-145-158:~/workspace/test$
```