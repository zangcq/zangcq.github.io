---
title: C++ const理解
tags: []
id: '805'
categories:
  - - programming
    - C/C++
date: 2019-05-14 10:13:44
---

const的作用 const是C语言的一种关键字，起受保护，防止以外的变动的作用！可以修饰变量，参数，返回值,甚至函数体。const可以提高程序的健壮性，你只管用到你想用的任何地方。

### (一)const修饰参数。

const只能修饰输入参数。

1、如果输入参数是指针型的，用const修饰可以防止指针被意外修改。

2、如果参数采用值传递的方式，无需const，因为函数自动产生临时变量复制该参数。

3、非内部数据类型的参数，需要临时对象复制参数，而临时对象的构造，析构，复制较为费时，因此建议采用前加const的引用方式传递非内部数据类型。而内部数据类型无需引用传递。

### (二)const修饰函数返回值。

1、函数返回const指针，表示该指针不能被改动，只能把该指针赋给const修饰的同类型指针变量。

2、函数返回值为值传递，函数会把返回值赋给外部临时变量，用const无意义！不管是内部还是非内部数据类型。

3、函数采用引用方式返回的场合不多，只出现在类的赋值函数中，目的是为了实现链式表达。

### (三)const+成员函数。

任何不修改数据成员的函数都应该声明为const类型，如果const成员函数修改了数据成员或者调用了其他函数修改数据成员，编译器都将报错！

class stack { 
  public: 
    int GetCount(void) const ;
  private: 
    int m\_num; 
  }; 
  
  int stack::GetCount(void) const { m\_num++; } 

编译器输出错误信息：

`error C2166: l-value specifies const object`。

### (四)const 修饰变量，表示该变量不能被修改。

1、const char \*p 表示 指向的内容不能改变

2、char \* const p，就是将P声明为常指针，它的地址不能改变，是固定的，但是它的内容可以改变。

3、这种const指针是前两种的结合,使得指向的内容和地址都不能发生变化.

 const double pi = 3.14159;   
 const double\* const pi\_ptr = pi;

 int a = 2;
 int b = 3;
 ​
 int\*              p1 = &a; // Modifiable pointer  modifiable value
 const int\*        p2 = &a; // Modifiable pointer  const value
 int\* const        p3 = &a; // Const pointer       modifiable value
 const int \* const p4 = &a; // Const pointer       const value
 ​
 \*p1 = 3; // Ok, modifiable left-value
 \*p2 = 4; // Error: non-modifiable left-value
 \*p3 = 5; // Ok
 \*p4 = 6; // Error
 ​
 p1 = &b; // Ok: modifiable pointer
 p2 = &b; // Ok
 p3 = &b; // Error
 p4 = &b; // Error

Ref

> [https://stackoverflow.com/questions/33261204/invalid-conversion-from-const-type-to-type](https://stackoverflow.com/questions/33261204/invalid-conversion-from-const-type-to-type)