---
title: Effective C++ 条款27 之 类型转换
tags:
  - C/C++
id: '388'
categories:
  - - programming
    - C/C++
date: 2017-09-12 08:33:46
---

# Effective C++ 之 类型转换

阿里面试过去好久了，可惜笔试做的太烂了，GG，不过还是要继续完善自己的知识体系的。

这个类型转换的问题，被面试官问到了，然后一脸尼克杨的蒙蔽表情。。

其实早就找到了，这个问题，一直因为忙别的，没有好好总结一下。。

### 含义

Effective C++条款27 尽量减少转型动作

C++的设计目标之一是，保证“类型错误”绝不可能发生。但是 转型 `casts`破坏了类型系统。

类型转换的含义就是通过改变一个变量的类型为 别的类型，从而改变变量的表达方式。 为了类型转换，我们通常会使用传统的类型转换符。

## 传统转型语法

```c++

// C语言风格
(T)expression //将 expression 转型为 T

// 函数风格
T(expression)
```

举个在C语言中的例子，我们把一个变量从 float 强制转换成 int 类型的时候，我们通常这样做：

```c++

int i;
float f;

// first 
i = (float)f;
// second
i = int(f);
```

这种方式对于已经是标准定义转换类型做的挺好，但是 对于我们在C++ 中自定义的类和 类的指针来说就不是很好用了。

## 新型转型

ANSI C++ 定义了四个新的类型转换符（详见 Effective C++ 第27 条）：

*   reinterpret\_cast(expression)
*   dynamic\_cast(expression)
*   static\_cast(expression)
*   const\_cast(expression)

那好我们分别介绍一下这几种类型转换的特点。

中间又被交叉面了两次，，又被提到了这个问题，，支支吾吾又没回答上来。。

### const\_cast

顾名思义，通常被用来将对象的常量性移除（cast away the constness）或者传递。说人话的就是把一个对象从常量对象变成可以修改的对象。

注意其他三种不能修改对象的常量性！

eg

```c++

class C{};

const C *a = new C;

C *b = const_cast<C *>(a);
```

指针b 就可以操作了。。

### dynamic\_cast

主要用来“向下安全转型”（safe downcasting）,也就是说来决定 某对象 是否归属继承体系中的某个类型。

只用于 对象的指针 和 引用。

当用于多态类型的时候，它允许任意的隐式类型转换，以及相反过程。

注意，在隐式转换的相反过程中，dynamic\_cast 会检查操作是否有效，他会检查转换是否会返回一个被请求的完整对象，如果不是一个有效的对象指针，返回值是`NULL`.

eg

*   对象的指针

```c#

//
class Base{
  virtual dummy(){};
};
class Derived:public Base{};

Base* b1 = new Derived;
Base* b2 = new Base;

Derived* d1 = dynamic_cast<Derived *>(b1);          // succeeds
Derived* d2 = dynamic_cast<Derived *>(b2);          // fails: returns 'NULL'
// b1 是 父类 类型的指针，指向一个 子类对象，然后可以转换成 子类的 指针。。这就是说可以安全向下
// b2 是 父类 类型的指针，指向一个 父类对象，那么这个父类对象的指针不能被转换，返回NULL
//理解起来可以这么想，，子类 继承了 父类，父类有的，子类一定有，但是子类有的父类不一定有。。
//这么就是说  子类对象的父类指针，可以变成 子类指针
// 父类对象的父类指针，不能变成 子类指针。。因为父类对象不一定是子类对象。
```

*   引用&

如果一个引用类型执行了类型转换并且这个转换是不可能的，一个bad\_cast的异常类型被抛出

```c++

class Base { virtual dummy() {} };
class Derived : public Base { };

Base* b1 = new Derived;
Base* b2 = new Base;

Derived d1 = dynamic_cast<Derived &*>(b1);          // succeeds
Derived d2 = dynamic_cast<Derived &*>(b2);          // fails: exception thrown
```

### static\_cast

static\_cast 允许执行任意的隐式转换 和 相反转换 动作。

应用到类指针上，，意思是 它允许 子类类型的指针 转换为父类类型的 指针，同时，，

它也允许 父类类型的 指针 转化为 子类类型的指针。。。

被转换的父类没有被检查是否与目的类型相一致。

```c++

class Base {};
class Derived : public Base {};

Base *a    = new Base;
Derived *b = static_cast<Derived *>(a);
/// 父类---->子类
/// 如果 提前知道了，可以这么做。。
```

'static\_cast'除了操作类型指针，也能用于执行类型定义的显式的转换，以及基础类型之间的标准转换

```c++

double d = 3.14159265;
int    i = static_cast<int>(d);
//有点强制的意思。。。
```

### reinterpret\_cast

`reinterpret_cast`转换一个指针为其它类型的指针。它也允许从一个指针转换为整数类型。反之亦然。

意思是说，这两个类型没有什么相关性，也可以相互转化，一个指针也能转成一个整数。

这个操作符能够在非相关的类型之间转换。操作结果只是简单的从一个指针到别的指针的值的二进制拷贝。在类型之间指向的内容不做任何类型的检查和转换。

如果情况是从一个指针 到 整型 的copy，内容的解释 是系统相关的，所以任何实现都不方便。

一个转换到足够大的整型能够包含它的指针是能够转换回有效的指针的。

```c++

class A {};
class B {};

A * a = new A;
B * b = reinterpret_cast<B *>(a);
//'reinterpret_cast'就像传统的类型转换一样对待所有指针的类型转换。
```

其实还是没有理解透彻，先记下来，，以后再回来看看吧

## reference

> 1.  《Effective C++》Scott Meyers
> 
> 1.  C++的四种cast操作符的区别--类型转换[http://www.cnblogs.com/welfare/articles/336091.html](http://www.cnblogs.com/welfare/articles/336091.html)