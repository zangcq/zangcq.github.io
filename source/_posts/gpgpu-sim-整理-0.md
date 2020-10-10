---
title: GPGPU-Sim 0 纵览
tags: []
id: '915'
categories:
  - - gpu-computing
    - GPGPU-Sim Notes
date: 2018-04-09 17:02:18
---

# GPGPU-Sim 纵览

#### Overview

写在前面的话，作为当年连一块`NVIDIA GPU`都没有的实验室初代探索者，我们只能通过模拟器来学习`GPU`如何工作的，三年来，从一开始的一穷二白到现在的`1080Ti`，也算是见证了实验室的发展。

言归正传，`GPGPU-Sim`是UBC [Tor Aamodt](http://www.ece.ubc.ca/~aamodt/publications.html) 组发表在[ISPASS2009](http://ieeexplore.ieee.org/document/4919648/) 会议上的一个`cycle`级别的模拟器，我在2015年下半年时引用量在800左右，到2018年4月 已经达到1086次引用。虽然模拟器的使用会时常被各种审稿人诟病，但是其相对于实际`GPU`来说，可以操作的空间很大，在体系结构的优化方面也是有可取之处的，因而从出现至今，已经成为最流行的`GPU`模拟器之一了。

#### 官方网站

> [http://www.gpgpu-sim.org/](http://www.gpgpu-sim.org/)

官方网站是一个对`GPGPU-Sim`的一个简介，一个架构图展示了其主要工作原理。那么它的源码在`github`上：

#### `github`源码

> [https://github.com/gpgpu-sim/](https://github.com/gpgpu-sim/)

对于`github`中，`gpgpu-sim distribution`是其源码，`ispass2009-benchmarks` 是其工作集。

由于`GPGPU-Sim`其模拟的架构是Fermi，对于GTX480等模拟的准确率较高，而对于其他架构，如Maxwell ，Pascal等架构，尚未给出模拟的准确率测试，但是在`gpgpu-sim distribution`的`dev`分支中有`GTX750Ti （Maxwell）`和`GTX1080Ti（Pascal）`的配置文件，因此，理论上说，也是可以模拟两种架构的性能的。

#### google group

> [https://groups.google.com/forum/#](https://groups.google.com/forum/#)!forum/gpgpu-sim

`gpgpu-sim`的`google group`实际上也是一个讨论问题的社区，基本上遇到的问题，搜索一下关键字，便能找到答案，对于实在无法解决的问题，也可以发帖求助，不过这个组的更新大概是每周一更，回复速度会比较慢。

#### Manual

[http://gpgpu-sim.org/manual/index.php/Main\_Page](http://gpgpu-sim.org/manual/index.php/Main_Page)

`Manual`即是`GPGPU-Sim`的官方手册，其内容不光介绍了模拟器的原理，同时也是极好的`GPU`体系结构的入门读物，科学网的前辈魏继增也翻译了这个手册。

> [http://blog.sciencenet.cn/home.php?mod=space&uid=1067211](http://blog.sciencenet.cn/home.php?mod=space&uid=1067211)

除了手册之外，还有一个`tutorial`会有一些如何使用的信息，并且讲述了其中集成的能耗测试模块。

> [http://www.gpgpu-sim.org/micro2012-tutorial/](http://www.gpgpu-sim.org/micro2012-tutorial/)