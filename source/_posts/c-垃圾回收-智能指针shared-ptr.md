---
title: C++ 垃圾回收 智能指针shared_ptr
tags:
  - C/C++
id: '276'
categories:
  - - programming
    - C/C++
date: 2017-08-07 23:33:42
---

# C++ 垃圾回收 智能指针shared\_ptr

> 转载自[http://www.cnblogs.com/qicosmos/p/3282779.html](http://www.cnblogs.com/qicosmos/p/3282779.html)

C#和Java 中都有自动垃圾回收机制，.net 和 java虚拟机可以管理分配的堆内存，在对象失去引用时自动回收，因此在这两种语言中，内存管理不是大问题。

C++中没有垃圾回收机制，必须自己去释放分配的堆内存，否则会造成内存泄露。

而这个问题，在C++中的解决办法就是，使用**智能指针**！因为智能指针可以自动删除分配的内存。

## 智能指针

是指向动态分配（堆）对象指针，用于生存期控制，能够确保自动正确的销毁动态分配的对象，防止内存泄露。

例如 shared\_ptr

![](https://i-msdn.sec.s-msft.com/dynimg/IC684644.jpeg)

它的一种通用实现技术是使用引用计数。每次使用它，内部的引用计数+1，每次 析构一次，内部引用计数-1，当减到0时，删除所指向的堆内存。

C++11之前，C++没有内置智能指针。只能借助boost的智能指针或者自己写。现在C++11已内置：

*   `std::shared_ptr`
*   `std::unique_ptr`
*   `std::weak_ptr`

那么下面分别说一下要怎么用

## `std::shared_ptr`

使用引用计数，每一个`shared_ptr`的拷贝都指向相同的内存。在最后一个 `shared_ptr`析构的时候，内存才会被释放。

1.  初始化

```c++

//智能指针的初始化
std::shared_ptr<int> p(new int(2));
std::shared_ptr<int> p2 = p;
std::shared_ptr<BaseConnector> m_connt = make_shared<Connector>(m_ios, m_strIP, m_port);
```

1.  智能指针中的原始指针，通过 get 获取
    
    ```c
    
    char* pData = pBuf.get();
    ```
    
2.  注意事项
    
    *   不要把原声指针给多个 shared\_ptr管理
    *   不要把this指针给shared\_ptr
    *   不要在函数实参里创建shared\_ptr
    *   在对象内部生成this的shared\_ptr

## `std::weak_ptr`

弱引用指针，用来监视智能指针，不会使引用计数加1。在访问所引用的对象前必须先转换为 std::shared\_ptr。

用来表达临时所有权的概念：当某个对象只有存在时才需要被访问，而且随时可能被他人删除时，可以使用

来跟踪该对象。需要获得临时所有权时，则将其转换为 std::shared\_ptr，此时如果原来的std::shared\_ptr 被销毁，则该对象的生命期将被延长至这个临时的 std::shared\_ptr 同样被销毁为止。

## `std::unique_ptr`

```c

unique_ptr不会共享它的指针。 无法将它复制到另一个unique_ptr， unique_ptr只能移动。 这意味着内存资源的所有权将转移到新的unique_ptr和原始unique_ptr不再拥有它
```

```c++

int* p = new int;
std::unique_ptr<int> ptr(p);
std::unique_ptr<int> ptr1 = ptr; //不能复制，编译报错

auto ptr2 = std::move(ptr); //转移所有权, 现在ptr那块内存归ptr2所有, ptr成为无效的指针.
```