---
title: C与CUDA混合编译动态链接文件.so
tags: []
id: '565'
categories:
  - - programming
    - C/C++
    - CUDA Programming
date: 2018-03-10 14:36:51
---

## C与CUDA混合编译动态链接文件`.so`

### 1.需求

由于需要生成动态链接库来被其他接口调用，因此我们需要编译成.so

### 2.实现

参考文献【1】用很简单的例子讲述了c和C++语言在Linux下如何编译成动态链接库。 方法很简单，只要加上编译选项`-shared`和`fPIC`即可

```bash

gcc test_a.c test_b.c test_c.c -fPIC -shared -o libtest.so
```

编译选项： `shared`：该选项指定生成动态连接库（让连接器生成T类型的导出符号表，有时候也生成弱连接W类型的导出符号），不用该标志外部程序无法连接。相当于一个可执行文件 `-fPIC`：表示编译为位置独立的代码，不用此选项的话编译后的代码是位置相关的所以动态载入时是通过代码拷贝的方式来满足不同进程的需要，而不能达到真正代码段共享的目的。 参考文献【2】将c和cuda代码编译成了.so文件，其实原理是一样的。 我们在用`nvcc`编译cuda代码时，加上`-Xcompiler -fPIC`即可

### 3.举例说明

我们有6个文件，前四个c文件，后2个cu文件。 1.编译c文件 加`fPIC`

```shell

gcc  -DOPENCV `pkg-config --cflags opencv`  -DGPU -I/usr/local/cuda/include/ -DCUDNN  -Wall -Wfatal-errors -Ofast -DOPENCV -fopenmp -DGPU -DCUDNN -I/usr/local/cudnn/include -c ./src/main.c -fPIC -o obj/main.o
 
gcc  -DOPENCV `pkg-config --cflags opencv`  -DGPU -I/usr/local/cuda/include/ -DCUDNN  -Wall -Wfatal-errors -Ofast -DOPENCV -fopenmp -DGPU -DCUDNN -I/usr/local/cudnn/include -c ./src/additionally.c   -fPIC -o obj/additionally.o

gcc  -DOPENCV `pkg-config --cflags opencv`  -DGPU -I/usr/local/cuda/include/ -DCUDNN  -Wall -Wfatal-errors -Ofast -DOPENCV -fopenmp -DGPU -DCUDNN -I/usr/local/cudnn/include -c ./src/box.c   -fPIC -o obj/box.o

gcc  -DOPENCV `pkg-config --cflags opencv`  -DGPU -I/usr/local/cuda/include/ -DCUDNN  -Wall -Wfatal-errors -Ofast -DOPENCV -fopenmp -DGPU -DCUDNN -I/usr/local/cudnn/include -c ./src/yolov2_forward_network.c  -fPIC  -o obj/yolov2_forward_network.o
```

2.编译cu文件 加`-Xcompiler -fPIC`

```shell

nvcc  -gencode arch=compute_61,code=[sm_61,compute_61]  -DOPENCV `pkg-config --cflags opencv`  -DGPU -I/usr/local/cuda/include/ -DCUDNN  --compiler-options "-Wall -Wfatal-errors -Ofast -DOPENCV -fopenmp -DGPU -DCUDNN -I/usr/local/cudnn/include" -c ./src/gpu.cu  -Xcompiler -fPIC -o obj/gpu.o

nvcc  -gencode arch=compute_61,code=[sm_61,compute_61]  -DOPENCV `pkg-config --cflags opencv`  -DGPU -I/usr/local/cuda/include/ -DCUDNN  --compiler-options "-Wall -Wfatal-errors -Ofast -DOPENCV -fopenmp -DGPU -DCUDNN -I/usr/local/cudnn/include" -c ./src/yolov2_forward_network_gpu.cu  -Xcompiler -fPIC -o obj/yolov2_forward_network_gpu.o
```

3.将所有生成的.o 文件，用gcc 加上 编译选项`-shared`和`fPIC`生成最后的.so

```shell

gcc  -DOPENCV `pkg-config --cflags opencv`  -DGPU -I/usr/local/cuda/include/ -DCUDNN  -Wall -Wfatal-errors -Ofast -DOPENCV -fopenmp -DGPU -DCUDNN -I/usr/local/cudnn/include obj/main.o obj/additionally.o obj/box.o obj/yolov2_forward_network.o obj/gpu.o obj/yolov2_forward_network_gpu.o -fPIC -shared -o darknet.so -lm -pthread  `pkg-config --libs opencv`  -lgomp -L/usr/local/cuda/lib64 -lcuda -lcudart -lcublas -lcurand -L/usr/local/cudnn/lib64 -lcudnn -lstdc++ 
```

### 4.总结

一句话总结就是，我们要想使用动态链接文件，必须将其编译为位置独立的代码，所以`fPIC`是必要的，而要生成`.so`文件，`shared`选项也是必须加的，所以记住这两点，然后再区分一下C和CU 选项的区别就可以了。

### Reference

\[1\][http://blog.sina.com.cn/s/blog\_54f82cc20101153x.html](http://blog.sina.com.cn/s/blog_54f82cc20101153x.html) \[2\][http://blog.csdn.net/u012816621/article/details/52334622](http://blog.csdn.net/u012816621/article/details/52334622)