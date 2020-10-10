---
title: CUDA 反编译工具
tags:
  - CUDA
  - GPU
id: '28'
categories:
  - - programming
    - CUDA Programming
date: 2017-06-06 14:42:14
---

# cuda binary

# 1.Overview

## 1.1什么是CUDA二进制文件

cuda 二进制文件 （.cubin .elf）是一种 ELF格式的文件，其中包含可执行代码部分，还包含了一些 符号、relocator、debug 信息等其他内容。 默认情况下，CUDA编译器 nvcc 可以讲cubin 文件，嵌入到 host 的可执行文件中。也可以 使用 nvcc -cubin 来编译直接得到 x.cubin 文件。 **注意：** 更多细节参见 nvcc 的用法。

## 1.2两种反编译工具

两个 反编译工具： cuobjdump and nvdisasm **1.2.1 相同点**：都可以 反编译 .cubin 文件 **1.2.2 不同点：** **1.cuobjdump可以 从 各种 二进制文件中，提取出 .ptx 代码 和 cubin 代码** 其中 包括 ：**1）Host binaries** ​

Executables
Object files
Static libraries

**2）External fatbinary files** nvdisasm 则不能。 **2.nvdisasm 可以进行 控制流分析并输出 和 显示高级选型**

# 2.cuobjdump

## 2.1用法

格式 ： 命令 选项 文件cuobjdump accepts a single input file each time it's run. The basic usage is as following:

cuobjdump \[options\] <file>

反编译->得到 sass 汇编代码To disassemble a standalone cubin or cubins embedded in a host executable and show CUDA assembly of the kernels, use the following command:

cuobjdump -sass <input file>

提取 elf 代码 To dump cuda elf sections in human readable format from a cubin file, use the following command:

cuobjdump -elf <cubin file>

提取 ptx 代码To extract ptx text from a host binary, use the following command:

cuobjdump -ptx <host binary>

**其他常用选项** 见 [nvidia-CUDA Binary Utilities-2.2. Command-line Options](http://docs.nvidia.com/cuda/cuda-binary-utilities/index.html#cuobjdump-options)

## 2.2例子

$ cuobjdump a.out  -sass 
Fatbin elf code: 
================ 
arch = sm\_20 
code version = \[1,7\] 
producer = cuda 
host = linux 
compile\_size = 64bit i
dentifier = add.cu 
code for sm\_20 
Function : \_Z3addPiS\_S\_ 
​
.headerflags @"EF\_CUDA\_SM20 EF\_CUDA\_PTX\_SM(EF\_CUDA\_SM20)" 
​
/\*0000\*/ MOV R1, c\[0x1\]\[0x100\]; /\* 0x2800440400005de4 \*/ 
/\*0008\*/ MOV R6, c\[0x0\]\[0x20\];  /\* 0x2800400080019de4 \*/ 
/\*0010\*/ MOV R7, c\[0x0\]\[0x24\];  /\* 0x280040009001dde4 \*/
/\*0020\*/ MOV R3, c\[0x0\]\[0x2c\];  /\* 0x28004000b000dde4 \*/ 
/\*0030\*/ MOV R4, c\[0x0\]\[0x30\];  /\* 0x28004000c0011de4 \*/
/\*0038\*/ LDU.E R2, \[R2\];        /\* 0x8c00000000209c85 \*/ 
/\*0050\*/ ST.E \[R4\], R0;         /\* 0x9400000000401c85 \*/ 
/\*0058\*/ EXIT;                  /\* 0x8000000000001de7 \*/

# 3.nvdisasm

## 3.1 Usage

使用格式nvdisasm accepts a single input file each time it's run. The basic usage is as following:

nvdisasm \[options\] <input cubin file>

常用选项

  -base  <value>  基地址
  -b  sm的版本
  -plr 打印寄存器的range

更多详见[nvidia-CUDA Binary Utilities-3.2. Command-line Options](http://docs.nvidia.com/cuda/cuda-binary-utilities/index.html#nvdisasm-options) 获取 kernel 的控制流图 To get the control flow graph of a kernel, use the following:

nvdisasm -cfg <input cubin file>

注意：控制流图 需要 Graphviz 中的 dot 命令 ，要先安装在电脑中才可用。 另 cubin 必须是 计算能力 3.0 以上的才可以

## 3.2 Example

其实 反编译的结果 是类似的 特别的是 其 生成的 控制流图。 eg

 nvdisasm -cfg a.cubin  dot -ocfg.png -Tpng