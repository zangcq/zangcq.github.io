---
title: TVM autotune优化的算子配置
tags: []
id: '1456'
categories:
  - - 机器学习
comments: false
date: 2020-09-11 12:23:48
---

```
{
    "input":[
                "vulkan -model=v1000",
                "conv2d_nchw.cuda",
                [
                    ["TENSOR", [1, 2048, 8, 8], "float32"],
                    ["TENSOR", [448, 2048, 1, 1], "float32"],
                    [1, 1],
                    [0, 0, 0, 0],
                    [1, 1],
                    "float32"
                ],
            {}],
    "config": {
        "index": 3546174,
        "code_hash": null,
        "entity": [
                    [
                        "tile_f",
                        "sp",
                        [-1, 8, 4, 1]
                    ],
                    [
                        "tile_y",
                        "sp",
                        [-1, 2, 2, 2]
                    ],
                    [
                        "tile_x",
                        "sp",
                        [-1, 1, 4, 1]
                    ],
                    [
                        "tile_rc",
                        "sp",
                        [-1, 4]
                    ],
                    [
                        "tile_ry",
                        "sp",
                        [-1, 1]
                    ],
                    [
                        "tile_rx",
                        "sp",
                        [-1, 1]
                    ],
                    [
                        "auto_unroll_max_step",
                        "ot",
                        1500
                    ],
                    [
                        "unroll_explicit",
                        "ot",
                        0
                    ]
                  ]
    },
    "result": [
                    [0.0012283149, 0.001328042, 0.0014977791000000001],
                    0,
                    4.963408708572388,
                    1584599323.7743187
    ],
    "version": 0.2,
    "tvm_version": "0.7.dev0"
 }
```