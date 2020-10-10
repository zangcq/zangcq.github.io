---
title: 编译优化技术-PGO
tags: []
id: '1249'
categories:
  - - 通用编译技术
comments: false
date: 2020-05-04 11:56:03
---

PGO 是 Profile Guided Optimization 的缩写，主要是用sampling的方法，对应用程序进行剖析，得到分析的数据，然后反馈给下一次编译。

传统编译都有实现

*   GCC

*   [https://developer.ibm.com/technologies/systems/articles/gcc-profile-guided-optimization-to-accelerate-aix-applications/](https://developer.ibm.com/technologies/systems/articles/gcc-profile-guided-optimization-to-accelerate-aix-applications/)

*   Clang
*   [https://clang.llvm.org/docs/UsersManual.html#profile-guided-optimization](https://clang.llvm.org/docs/UsersManual.html#profile-guided-optimization)

*   android 中如何使用 clang pgo进行优化：
*   [https://source.android.com/devices/tech/perf/pgo](https://source.android.com/devices/tech/perf/pgo)

以GCC为例主要工作流程

1、采样编译：

修改COMMON\_FLAGS 加上-fprofile-generate=(dir)选项，其中dir为存放采样文件的目录

例如：

COMMON\_FLAGS="$COMMON\_FLAGS  -fprofile-generate=/u01/profile"

2、运行采样

编译完成后按正常测试流程跑完测试用例，所有的采样文件存放在之前指定的目录中，格式为#xx#xx#xx.cc.gcda, 对每一个执行到的源代码文件都会生成一个对应的gcda的文件。

3、采样数据合并

若进行了多次运行采样，比如分别存放在目录profile\_data/1, profile\_data/2, profile\_data/3中，可通过如下命令进行合并

gcov-tool merge profile\_data/1 profile\_data/2 -o temp1
gcov-tool merge temp1 profile\_data/3 -o profile\_merged

4、优化编译：

修改COMMON\_FLAGS，增加-fprofile-use=(dir) -Wno-missing-profile -fprofile-correction, 其中dir就是gcda文件的目录，若涉及多次采样则为最终merge后的目录

例如：

COMMON\_FLAGS="$COMMON\_FLAGSc -fprofile-use=/u01/profile -Wno-missing-profile -fprofile-correction"

编译后即已经应用了pgo优化