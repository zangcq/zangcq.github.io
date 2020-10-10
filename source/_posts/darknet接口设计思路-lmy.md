---
title: darknet接口设计思路-lmy
tags: []
id: '162'
categories:
  - - 机器学习
date: 2018-05-19 20:26:10
---

# darknet接口设计思路

\[TOC\]

## 概述

经过分析，我首先承认原作者提供的接口具有普适性、易读性和示范性，但是终归只是起示范作用，在性能方面是低效的，主要体现在下面几个方面

*   强调顺序性：充分利用了框架中定义的函数，按照步骤一步一步的进行参数传递，计算，结果返回，然而这中间很多步骤存在大量的冗余计算。
    
*   框架中边缘功能API实现低效：为了充分发挥平台的算力，我们需要尽量减少额外计算的时间，让GPU进行网络传播计算的时间占比更大，然而，darknet这个框架的虽然充分利用了cuda+cudnn来充分发挥GPU算力，但是对图像预处理，网络加载等工作的实现效率极低
    
    eg:
    
    ```C
    
            image im = load_image_color(path,0,0);
            image sized = letterbox_image(im, net->w, net->h);
    ```
    
    这两行代码是每一次图像读取进来后进行处理的函数，之后`sized`这个图片才会被作为网络输入，关注一下他的实现：
    
    ```c
    
    image load_image_color(char *filename, int w, int h)
    {
        return load_image(filename, w, h, 3);
    }
    // ... ...
    image load_image(char *filename, int w, int h, int c) //这里可以搞个多线程
    {
    #ifdef OPENCV
        image out = load_image_cv(filename, c);
    #else
        image out = load_image_stb(filename, c);
    #endif
    
        if((h && w) && (h != out.h  w != out.w)){
            image resized = resize_image(out, w, h);
            free_image(out);
            out = resized;
        }
        return out;
    }
    // ... ...
    image load_image_stb(char *filename, int channels) //无论如何，都逃不过for循环内存拷贝的噩梦
    {
        int w, h, c;
        unsigned char *data = stbi_load(filename, &w, &h, &c, channels);
        if (!data) {
            fprintf(stderr, "Cannot load image \"%s\"\nSTB Reason: %s\n", filename, stbi_failure_reason());
            exit(0);
        }
        if(channels) c = channels;
        int i,j,k;
        image im = make_image(w, h, c);
        for(k = 0; k < c; ++k){
            for(j = 0; j < h; ++j){
                for(i = 0; i < w; ++i){
                    int dst_index = i + w*j + w*h*k;
                    int src_index = k + c*i + c*w*j;
                    im.data[dst_index] = (float)data[src_index]/255.;
                }
            }
        }
        free(data);
        return im;
    }
    ```
    
    首先这是整个load\_image的过程，这里我选择展示了他使用stb API的部分，使用opencv的算法大同小异，我总结了一下他的特点：
    
    *   为了API通用性而进行的连续函数转发：
        
        中间函数很可能还被其他很多函数用到，所以为了减少重复编程，作者采用了多层转发的方式，加载一张的图片，就要进行四层函数调用，而且返回值竟然都是结构体，效率不敢恭维
        
    *   极度低效的图片存储格式转换：
        
        这个是整个框架用到比赛中最为致命的缺陷，arm架构本来就没有x86那样单核性能强大，这里还将所有的访存和计算全部交给一个线程来完成，而且更为致命的是先读，再计算，最后写，而且读出的位置和写入的位置完全不相邻，这样编译器的自动循环展开都不好用
        
    
    ```C
    
    image letterbox_image(image im, int w, int h)
    {
        int new_w = im.w;
        int new_h = im.h;
        if (((float)w/im.w) < ((float)h/im.h)) {
            new_w = w;
            new_h = (im.h * w)/im.w;
        } else {
            new_h = h;
            new_w = (im.w * h)/im.h;
        }
        image resized = resize_image(im, new_w, new_h);
        image boxed = make_image(w, h, im.c);
        fill_image(boxed, .5);
        //int i;
        //for(i = 0; i < boxed.w*boxed.h*boxed.c; ++i) boxed.data[i] = 0;
        embed_image(resized, boxed, (w-new_w)/2, (h-new_h)/2); 
        free_image(resized);
        return boxed;
    }
    // ... ...
    image resize_image(image im, int w, int h)
    {
        image resized = make_image(w, h, im.c);   
        image part = make_image(w, im.h, im.c);
        int r, c, k;
        float w_scale = (float)(im.w - 1) / (w - 1);
        float h_scale = (float)(im.h - 1) / (h - 1);
        //为了保证访存效率，都是按照行遍历
        //重置宽度
        for(k = 0; k < im.c; ++k){
            for(r = 0; r < im.h; ++r){
                for(c = 0; c < w; ++c){
                    float val = 0;
                    if(c == w-1  im.w == 1){
                        val = get_pixel(im, im.w-1, r, k);
                    } else {//重置方式
                        float sx = c*w_scale;//利用新图片中的坐标找到原图中坐标的位置(一般不是整数)
                        int ix = (int) sx;//将分数坐标分成整数和小数部分
                        float dx = sx - ix;
                        val = (1 - dx) * get_pixel(im, ix, r, k) + dx * get_pixel(im, ix+1, r, k);//整数部分作为真正坐标，小数部分作为其和相邻像素的混合系数
                    }
                    set_pixel(part, c, r, k, val);
                }
            }
        }
        //重置高度
        for(k = 0; k < im.c; ++k){
            for(r = 0; r < h; ++r){
                float sy = r*h_scale;
                int iy = (int) sy;
                float dy = sy - iy;
                for(c = 0; c < w; ++c){//将主数据放入
                    float val = (1-dy) * get_pixel(part, c, iy, k);
                    set_pixel(resized, c, r, k, val);
                }
                if(r == h-1  im.h == 1) continue;
                for(c = 0; c < w; ++c){//将额外数据加上
                    float val = dy * get_pixel(part, c, iy+1, k);
                    add_pixel(resized, c, r, k, val);
                }
            }
        }
    
        free_image(part);
        return resized;
    }
    // ... ...
    void embed_image(image source, image dest, int dx, int dy)
    {
        int x,y,k;
        for(k = 0; k < source.c; ++k){
            for(y = 0; y < source.h; ++y){
                for(x = 0; x < source.w; ++x){
                    float val = get_pixel(source, x,y,k);
                    set_pixel(dest, dx+x, dy+y, k, val);
                }
            }
        }
    }
    ```
    
    然后是`letterbox_image`的流程，实现的功能是：
    
    *   使用二线性插值法将图片的长边放缩到网络输入层的尺寸
    *   将图片嵌入和网络输入层一样大的一张灰色图片
    
    整个实现槽点太多：
    
    *   低效的函数调用：仍然是老问题，每个函数仅完成一项工作，返回一个结构体
    *   滥用单核性能：依旧是满眼for for for
    *   大量中间结果：整个过程中创建了许多image结构体，很多就在用完后就直接释放掉了，这个又申请又释放的过程耽误时间

综上所述，这就是我了解的框架边缘API的不足，上述函数全部定义在`iamge.c`中

## 早先版本中存在的问题

简要评价一下我们最初版本的代码：

*   不完全符合规则：
    
    我们并没有利用官方给出框架的输入作为深度学习框架的输入，也没有将识别结果存放到官方给出的结果数组中。我们仅仅从官方框架那里获得了文件名，并利用文件名重新读出了图片，完成识别，把结果存在自己的数组中，然后在将官方给出的输出函数中输入参数掉包
    
*   使用了低效的边缘API：我们没有对作者给出的图像预处理算法进行任何修改，依旧是低效的样子，无法提高并行性
    
*   Python与C语言格式转化耽误时间：我们将深度学习框架编译成so，并使用Python的ctypes库进行调用，这中间存在着大量的格式转换，每次调用都要进行，降低了效率
    

在充分考虑CPU利用的基础上，对整个比赛代码的边缘部分进行了重新设计

## 整体流程设计

简单描述一下我设计的计算流程

*   为了避免低效的ctypes库调用，我选择将C的代码包装成Python扩展，实现Python与我们框架的无缝衔接
*   重新利用了官方提供的网络输入，使用并行编程完成图片的格式转换
*   网络传播计算和图片预处理流水工作，即CPU和GPU计算的重叠
*   识别结果通过Python提供的相关函数进行格式转化，从C语言环境返回到Python环境，存入官方给出的输出数组

## 并行性设计

使用多线程对Python数组进行处理，转换成网络输入的大小，省去中间一切函数调用

实现是3线程或6线程，完成对网络输入的格式转换

*   工作分配是按通道进行分配，每个通道1~2个线程
*   每个线程首先从Python数组中取出自己负责区域的像素，按照imge结体的内部各式存入本地缓冲区
*   利用缓冲区中的数据完成该区域的二线性插值计算，将结果放入线程间共享的输入缓冲区，也就是作为结果的image结构体，交给GPU进行运算

6线程任务分配细节：

*   分到同一个通道的两个线程，按照行将图片分成两半（image结构体按通道、行、列的顺序存取），最大程度避免访存冲突和伪共享现象
    
*   二线性插值运算的问题：一个线程完成自己负责区域的二线性插值运算的时候，不会用到其他线程的数据，这是由我们网络的尺寸和图片尺寸决定的。
    
    一个通道中，一号线程负责0~116行的计算，而根据二线性插值法，其对应到原图的0～179行；二号线程对应到180~233。正好都是它们自己的缓冲区中的数据
    

## 流水方式设计

整个接口中用到了如下线程：

*   Python主线程，负责输入图片和获取结果，本质上就是`/usr/bin/python`这个程序
*   图像预处理线程3~6个，完成上一节提到的工作
*   识别线程1个，因为GPU只有一个（也很难说多加一个能不能提高性能），等待图片识别线程完成工作，对图片进行识别

之间的同步关系如下：

*   主线程进入本模块，将Python数组（一个batch的图片）的数据域提交给图像预处理线程，开始工作，开始等待识别线程完成工作，取出结果返回
*   识别线程等待主线程输入，得到输入后开始工作，完成一张图片后紧接着开始下一张，直到batch处理完成，等待主线程信号。在处理图片的同时记录每个线程完成图片的情况，最后一个完成一张图片的线程，需要把这张图片交给识别线程
*   识别线程只等待预处理线程的信号，拿到图片开始处理，返回结果，继续等待

上面这个过程已经实现了初级的流水，但是经过测量，预处理线程的速度实在太快，耗时最长的成了官方代码中的`cv.imread`。为了进一步提高性能，我设计了一个可能违反规则的版本（论违规程度应该不超过最初版本），与上面描述的过程的差别如下：

*   主线程不再等待识别线程完成，而是直接返回，不向官方提供的结果数组中存结果
*   识别线程按照Python数组格式将识别结果存入模块内的全局数组
*   官方调用写结果函数的时候，官方的结果数组与模块中存储的数组掉包

这样就实现了全面的图片读取+预处理和识别的全面并行，性能有了不小的提高

## 下一步工作展望

我认为框架的边缘API尚且如此，核心的运算API性能可能也有提高的余地，尤其是各个层`forward`和`backward`的计算中可能还有优化的空间