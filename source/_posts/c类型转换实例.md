---
title: C++类型转换实例
tags:
  - C/C++
id: '657'
categories:
  - - programming
    - C/C++
date: 2018-10-09 20:34:21
---

最近遇到了类型转换的问题，记录一下

#### 1\. 问题：如何将 float 转成 void\*

#### 2\. 分析

**float** 4字节

**指针** 根据操作系统确定大小

*   64位 8字节
*   32位 4字节

结论：可以进行转换，不会丢失精度。

**如果丢失精度应怎样处理？**

顺便回顾一下float类型的内存表示

ruanyifeng 解释的较详细

> [http://www.ruanyifeng.com/blog/2010/06/ieee\_floating-point\_representation.html](http://www.ruanyifeng.com/blog/2010/06/ieee_floating-point_representation.html)

特殊值

> [https://blog.csdn.net/eickandy/article/details/48376435](https://blog.csdn.net/eickandy/article/details/48376435)

开源中国的在线转换器

> [http://tool.oschina.net/hexconvert](http://tool.oschina.net/hexconvert)

#### 3\. 强制转换

1.  yym
    
    line 5 说明
    
    *   (&p) 取出 void \* 指针的地址
    *   (float \*)(&p) 将 void \*的地址 强制转换 为float \* 类型
    *   \*(float \*)(&p) 用\* 来从地址中取值
    
    > [http://www.runoob.com/cplusplus/cpp-pointers.html](http://www.runoob.com/cplusplus/cpp-pointers.html)
    

```c++
#include <iostream>
int main() {
  void *p = nullptr;
  float f = 0.01;
  *(float *)(&p) = f;
  std::cout << "p = " << p << std::endl;

  float f2 = *(float *)(&p);
  std::cout << "f2 = " << f2 << std::endl;
}
```

1.  Memory copy

```c++
#include <iostream>
int main() {
  void *p = nullptr;
  float f = 0.01;
  *(float *)(&p) = f;
  std::memcpy(&p, &f, sizeof f);
  std::cout << "p = " << p << std::endl;

  float f2 = *(float *)(&p);
  std::cout << "f2 = " << f2 << std::endl;
}
```

*   output

```shell
zangchuanqideMacBook-Pro:~ zcq$ ./a.out
p = 0x3c23d70a
f2 = 0.01
```

回顾C++四种强制转换的方法

> [https://blog.csdn.net/ydar95/article/details/69822540](https://blog.csdn.net/ydar95/article/details/69822540)
> 
> [https://en.cppreference.com/w/cpp/language/reinterpret\_cast](https://en.cppreference.com/w/cpp/language/reinterpret_cast)
> 
> [https://www.cnblogs.com/ider/archive/2011/08/05/cpp\_cast\_operator\_part6.html](https://www.cnblogs.com/ider/archive/2011/08/05/cpp_cast_operator_part6.html)

#### 4\. 其他栗子

1、指针类型强制转换：

```c++
int m;
int *pm = &m;
char *cp = (char *)&m;

// pm指向一个整型，cp指向整型数的第一个字节
```

2、结构体之间的强制转换

```c++
struct str1 a;
struct str2 b;

a=(struct str1) b;             //this is wrong
a=*((struct str1*)&b);         //this is correct

```

> [https://blog.csdn.net/mhjcumt/article/details/7355127](https://blog.csdn.net/mhjcumt/article/details/7355127)