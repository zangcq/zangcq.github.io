---
title: perf 工具使用和火焰图生成
tags: []
id: '746'
categories:
  - - 工欲善其事必先利其器
date: 2019-03-04 23:11:33
---

Perf 阶段

*   生成perf.data
    *   `perf record --call-graph dwarf python concat.py`
*   \-g 表示生成调用关系。
    *   `perf record -g python concat.py`
*   \-i 代表查看其调用关系。
    *   `perf report -i perf.data`
*   用perf script工具对perf.data进行解析
    *   `perf script -i perf.data &> perf.unfold`

FlameGraph 阶段

1.  克隆工程
    1.  `git clone <https://github.com/brendangregg/FlameGraph.git>` Perl 语言实现，无须安装其他依赖。
2.  将perf.unfold中的符号进行折叠：
    1.  `./stackcollapse-perf.pl perf.unfold &> perf.folded`
3.  最后生成svg图：
    1.  `./flamegraph.pl perf.folded > perf.svg`

> [https://www.cnblogs.com/happyliu/p/6142929.html](https://www.cnblogs.com/happyliu/p/6142929.html)
> 
> [https://nanxiao.me/perf-note-4-profile-application/](https://nanxiao.me/perf-note-4-profile-application/)
> 
> 火焰图使用reference

##### tensorflow vlog 打印级别

export TF\_CPP\_MIN\_VLOG\_LEVEL=5

##### tensorflow 打印张量时，输出不完全，总有省略号怎么办

**完整输出 tensor内容**

import numpy as np  
np.set\_printoptions(threshold=np.inf)