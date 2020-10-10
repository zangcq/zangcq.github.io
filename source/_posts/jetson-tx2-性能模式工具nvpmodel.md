---
title: Jetson tx2 性能模式工具nvpmodel
tags:
  - Jetson
  - tx2
id: '490'
categories:
  - - gpu-computing
    - Jetson TX1-2
date: 2017-12-18 14:28:10
---

## Jetson tx2 性能模式工具`nvpmodel`

\[TOC\]

`Jetson Tegra`系统的应用涵盖越来越广，相应用户对性能和功耗的要求也呈现多样化。为此`NVIDIA`提供一种新的命令行工具，可以方便地让用户配置CPU状态，以最大限度地提高不同场景下的性能和能耗。 `Jetson TX2`由一个`GPU`和一个`CPU`集群组成。 `CPU`集群由`双核丹佛2`处理器和四核`ARM Cortex-A57`组成，通过高性能互连架构连接。`GPU` 是由两个`Pascal` 架构的`SM`组成 , 计算能力 `6.2`,还有一些用来加速特定应用的`ASIC`电路.架构图如下

### TX2架构图

![这里写图片描述](http://img.blog.csdn.net/20171218141114577?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvZGFyazU2Njk=/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)

### 性能模式列表

TX2 拥有6个`CPU`核心和一个`GPU`，你可以不必自行运行所有性能/功耗来测试最佳的运行状态，因为`NVIDIA`的新的命令工具`Nvpmodel`，提供了5种模式。在`Jetson TX2`上。 下表列出了CPU内核的模式以及正在使用的CPU和GPU的最大频率。

mode

Mode Name

Denver 2

Frequency

ARM A57

Frequency

GPU Frequency

0

Max-N

2

2.0 GHz

4

2.0 GHz

1.30 Ghz

1

Max-Q

0

4

1.2 GHz

0.85 Ghz

2

Max-P Core-All

2

1.4 GHz

4

1.4 GHz

1.12 Ghz

3

Max-P ARM

0

4

2.0 GHz

1.12 Ghz

4

Max-P Denver

2

2.0 GHz

0

1.12 Ghz

TX2默认模式是只开4个`CPU`, 所以你如果要打开其最大性能的话,那就试试`nvpmodel` ,切换一下模式吧.

### 用法

```shell

nvidia@tegra-ubuntu:~$ sudo nvpmodel 
[sudo] password for nvidia: 
Nvidia Power Model Tool Version 1.0.0
Usage:
nvpmodel [-h  --help] [--verbose] [-q  --query] [-p  --parse] [-u  --udata]
[-m  --mode <mode>] [-f  --conf <filename>] [-o  --os <android,l4t>]
-h, --help:
Print this help info.
--verbose:
Enable verbose log.
-p, --parse:
Parse the config file only. Recommended to enable verbose log.
-m, --mode <mode>:
<mode> is one of the integer POWER_MODEL ID defined in config file. Switch to the specified power mode.
-f, --conf:
explicitly specify the config file.            
If it is the only option, then it sets the power mode as default mode configured in the file.            
This option can be used for developer usage to specify a config file other than the default one.
-o, --os <android,l4t>:
Perform OS specific operations for power model settings. Argument is case insensitive.
-q, --query:
Query the current power mode.
-w, --wait:
delay exectuion by specified amount of seconds.
-u, --udata:
specify the absolute path for user data file when set or query power mode.
```

### 举例

1.  `nvpmodel -m 2`切换模式
    
    ​切换模式到`Max-P Core-All`
    

1.  比如说查看当前模式`nvpmodel -q --verbose`,并打印信息
    
    ```shell
    
    nvidia@tegra-ubuntu:~$ sudo nvpmodel -q --verbose
    NVPM VERB: parsing done for /etc/nvpmodel.conf
    NVPM VERB: Current mode: NV Power Mode: MAXN
    0
    NVPM VERB: PM_CONFIG: DEFAULT=MAXP_CORE_ARM(3)
    NVPM VERB: ACTIVE=MAXN(0)
    NVPM VERB: POWER_MODEL: ID=0 NAME=MAXN
    NVPM VERB: /sys/devices/system/cpu/cpu1/online 1
    NVPM VERB: value = 1
    NVPM VERB: /sys/devices/system/cpu/cpu2/online 1
    NVPM VERB: value = 1
    NVPM VERB: /sys/devices/system/cpu/cpu3/online 1
    NVPM VERB: value = 1
    NVPM VERB: /sys/devices/system/cpu/cpu4/online 1
    NVPM VERB: value = 1
    NVPM VERB: /sys/devices/system/cpu/cpu5/online 1
    NVPM VERB: value = 1
    NVPM VERB: /sys/devices/system/cpu/cpu0/cpufreq/scaling_min_freq 0
    NVPM VERB: value = 345600
    NVPM VERB: /sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq 2035200
    NVPM VERB: value = 2035200
    NVPM VERB: /sys/devices/system/cpu/cpu1/cpufreq/scaling_min_freq 0
    NVPM VERB: value = 345600
    NVPM VERB: /sys/devices/system/cpu/cpu1/cpufreq/scaling_max_freq 2035200
    NVPM VERB: value = 2035200
    NVPM VERB: /sys/devices/17000000.gp10b/devfreq/17000000.gp10b/min_freq 0
    NVPM VERB: value = 140250000
    NVPM VERB: /sys/devices/17000000.gp10b/devfreq/17000000.gp10b/max_freq 1300500000
    NVPM VERB: value = 1300500000
    NVPM VERB: /sys/kernel/nvpmodel_emc_cap/emc_iso_cap 0
    NVPM VERB: value = 0
    NVPM VERB: 
    ```
    
2.  更多例子
    
    ```shell
    
    nvpmodel -m 2: switch to POWER_MODEL ID=2 of which settings are defined in the default configuration file.
    nvpmodel -m 2 -o android: switch to POWER_MODEL ID=2 and perform Android specific operations for power mode.
    nvpmodel -m 2 -f pm.conf: switch to POWER_MODEL ID=2 of which settings are defined in pm.conf.
    nvpmodel -m 2 -u /data/status: switch to POWER_MODEL ID=2 and store the active mode as user settings in /data/status.
    nvpmodel -f pm.conf: read the active mode in user data file and set it as the power mode which is configured in pm.conf.            
    If user data file does not exist or the active mode value is invalid, set defalut mode instead.
    nvpmodel -q: print the current power mode.
    nvpmodel -q --verbose: print the current power mode with verbose info.
    nvpmodel -p -f pm.conf: parse pm.conf and print the result.
    ```
    
    ​
    

### 参考文献

> [https://devblogs.nvidia.com/parallelforall/jetson-tx2-delivers-twice-intelligence-edge/](https://devblogs.nvidia.com/parallelforall/jetson-tx2-delivers-twice-intelligence-edge/)
> 
> [http://www.jetsonhacks.com/2017/03/25/nvpmodel-nvidia-jetson-tx2-development-kit/](http://www.jetsonhacks.com/2017/03/25/nvpmodel-nvidia-jetson-tx2-development-kit/)