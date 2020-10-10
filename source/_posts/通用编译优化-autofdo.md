---
title: 通用编译优化-AutoFDO学习
tags: []
id: '1252'
categories:
  - - 通用编译技术
comments: false
date: 2020-05-04 12:03:00
---

### 概念

AutoFDO是指基于程序性能分析工具的反馈式编译优化。相比基于程序插桩的PGO优化，AutoFDO可以对优化过的程序进行性能分析；利用如\`perf\`工具来收集程序的性能信息，整体开销在2%以内，可以部署在真实的产品线上，利用程序在生产环境的性能信息对程序进行更精准的优化。

X86上使用处理器的BR\_INST\_RETIRED:TAKEN事件信息，主要记录了跳转前后的pc地址；google提供了create\_gcov工具来将perf.data转化为编译需要的afdo文件。

详见：[https://github.com/VictorRodriguez/autofdo\_tutorial](https://github.com/VictorRodriguez/autofdo_tutorial)

在arm64上有相应的coresight etm来记录运行轨迹，再生成AutoFDO需要的afdo文件。

参考：[https://github.com/Linaro/OpenCSD/blob/master/decoder/tests/auto-fdo/autofdo.md](https://github.com/Linaro/OpenCSD/blob/master/decoder/tests/auto-fdo/autofdo.md)

但coresight etm在当前鲲鹏服务器并没有支持，影响了AutoFDO在当前arm64上的使用。

### AutoFDO文件分析

通过分析perf.data生成的afdo文件，发现afdo文件记录了函数，以及对应源码行之间的跳转信息。这些信息仅与源代码相关，与编译链接地址和架构无关，所以推理可以将x86上生成的afdo用于使用相同源码的arm工程。

### 示例

下载autofdo\_tutorial，并运行make release。

make过程中会下载[https://github.com/andikleen/pmu-tools.git](https://github.com/andikleen/pmu-tools.git)，

和[https://github.com/google/autofdo](https://github.com/google/autofdo)，并编译autofdo工具。

可以按照下列顺序来生成bubble-sort的各个对比版本。

#编译bubble\_sort的O3版本
gcc -std=gnu99 -Iinclude -pedantic -Wall -Wextra -march=native -ggdb3 -lm -O3 -o bubble\_sort\_O3 src/bubble\_sort.c src/debug.c

#运行perf，并生成fbdata.afdo

/tmp/pmu-tools/ocperf.py record -b -e br\_inst\_retired.near\_taken -- ./bubble\_sort\_O3
/tmp/autofdo/create\_gcov --binary=./bubble\_sort --profile=perf.data --gcov=bubble\_sort.afdo -gcov\_version=1
/tmp/autofdo/profile\_merger -gcov\_version=1 \*.afdo

#使用fbdata.afdo，生成bubble\_sort autofdo版本

gcc -std=gnu99 -Iinclude -pedantic -Wall -Wextra -march=native -ggdb3 -lm -O3 -fauto-profile=fbdata.afdo -o bubble\_sort\_autofdo src/bubble\_sort.c src/debug.c

运行O3和autofdo版本，可以发现autofdo相比O3又提高了6%左右。

$./bubble\_sort\_O3
Bubble sorting array of 30000 elements
2002 ms
$./bubble\_sort\_autofdo
Bubble sorting array of 30000 elements
1874 ms

将fbdata.afdo文件拷贝到arm64环境下，生成autofdo版本。可以发现arm64下也获得相应的性能提升。

$./bubble\_sort\_O3
Bubble sorting array of 30000 elements
2110 ms
$./bubble\_sort\_autofdo
Bubble sorting array of 30000 elements
1882 ms