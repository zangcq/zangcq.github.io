---
title: perl syntax 1
tags:
  - perl
id: '303'
categories:
  - - programming
    - Perl
  - - 程序人生
date: 2017-08-10 17:17:37
---

## 数据类型

```perl

#!/usr/bin/perl

#context 上下文
#perl 最独特的特性就在于 它的代码对于上下文是敏感的。
#每个perl的表达式要么在 scalar 上下文中求值，要么在列表上下文求值

my $scalar = "mendeleev";#赋值

#初始化 array 和 hash
my @array = ("Alpha", "Beta", "Gamma", "Pie");
my %hash = ("Alpha" => "Beta", "Gamma" => "Pie");

#在scalar上下文中求值的列表表达式会返回 列表 中的最后一个scalar：
my $scalar = ("Alpha", "Beta", "Gamma", "Pie");# $scalar的值现在是"Pie"

#在scalar上下文中求值的array（还记得array和列表不同吗？）表达式返回该数组的长度：
my @array = ("Alpha", "Beta", "Gamma", "Pie");
my $scalar = @array; # $scalar的值现在是4

#print内置函数在列表上下文中求对所有的参数求值。
#事实上，print能够接受无限个参数的列表，并且一个接一个地打印它们，这就意味着我们可以直接用它来打印array：

my @array = ("Alpha", "Beta", "Goo");
my $scalar = "-X-";
print @array;              # "AlphaBetaGoo";
print $scalar, @array, 98; # "-X-AlphaBetaGoo98";


#引用和嵌套数据结构

#列表无法包含列表作为其元素，array也同样无法包含其他array和hash作为其元素，它们只能包含scalar。

#那么我们就可以用，scalar来 进行引用和赋值

#声明数据结构
```

## Array函数

### 原地（In-place）array修改函数

我们用`@stack`来演示这些函数：

```perl

my @stack = ("Fred", "Eileen", "Denise", "Charlie");
#这个数组 ，可以理解为一个栈，Fred 为栈底元素、Charlie 为 栈顶元素
print @stack; # "FredEileenDeniseCharlie"
```

`pop`抽取并返回array的最后一个元素，可以认为是栈顶的元素：

```perl

print pop @stack; # "Charlie"
print @stack;     # "FredEileenDenise"
#出栈，从栈顶 取出 元素并返回
```

`push`向array末尾添加一个元素：

```perl

push @stack, "Bob", "Alice";
print @stack; # "FredEileenDeniseBobAlice"
#入栈，在栈顶位置，添加元素到数组
```

`shift`抽取并返回array的第一个元素：

```perl

print shift @stack; # "Fred"
print @stack;       # "EileenDeniseBobAlice"
#相当于一个 有头指针单链表，在头部位置 取出元素并且返回
```

`unshift`向array的头部插入一个元素：

```perl

unshift @stack, "Hank", "Grace";
print @stack; # "HankGraceEileenDeniseBobAlice"
#相当于一个 单链表，从头部 插入元素
```

`pop`、`push`、`shift`和`unshift`都是`splice`的特例。`splice`返回删除的一个array的切片，并且用另一个array的切片在原array中替换之：

```perl

print splice(@stack, 1, 4, "<<<", ">>>"); # "GraceEileenDeniseBob"
print @stack;                             # "Hank<<<>>>Alice"
#用 <<< >>> 替换 从 stack[1] 到stack[4]之间的 字符串
```

### 从现有的array创建新的array

Perl提供下面这些函数，可以操作现有的array产生新的array。

`join`函数把多个字符串连接成一个字符串：

```perl

my @elements = ("Antimony", "Arsenic", "Aluminum", "Selenium");
print @elements;             # "AntimonyArsenicAluminumSelenium"
print "@elements";           # "Antimony Arsenic Aluminum Selenium"
print join(", ", @elements); # "Antimony, Arsenic, Aluminum, Selenium"
#将 elements 数组中 各个元素 用", ” 连成一个字符串
#可以把 第一个参数 理解成胶水，通过他来将 各个元素 粘起来；
```

在列表上下文，`reverse`函数把传入的列表逆序返回，在scalar上下文，`reverse`先把字符串列表连接起来，再将这个字符串反转。

```perl

print reverse("Hello", "World");        # "WorldHello"
print reverse("HelloWorld");            # "HelloWorld"
print scalar reverse("HelloWorld");     # "dlroWolleH"
print scalar reverse("Hello", "World"); # "dlroWolleH"
#逆序字符串，很好理解
```

`map`函数接受一个array，并将一个操作应用于这个array中的每一个scalar `$_`，然后返回用这些scalar创建的array。这个操作用在花括号中的一个表达式来表示：

```perl

my @capitals = ("Baton Rouge", "Indianapolis", "Columbus", "Montgomery", "Helena", "Denver", "Boise");

print join ", ", map { uc $_ } @capitals;
#perl uc()函数例子，uc()函数实例代码 - 返回一个大写的版本EXPR，或$_ 如果没有指定
# "BATON ROUGE, INDIANAPOLIS, COLUMBUS, MONTGOMERY, HELENA, DENVER, BOISE"
```

`grep`函数接受一个array，并返回一个经过筛选的array。语法与`map`类似，而第二个参数会对array中的每个scalar `$_`求值，如果返回true，这个scalar就会被放到输出array中，否则就不会。

```perl

print join ", ", grep { length $_ == 6 } @capitals;
# "Helena, Denver"
#筛选出 字符长度等于 6 的 元素
```

显然，返回的array长度是_满足条件的元素个数_，这就意味着你可以用`grep`检查array中是否包含某个元素：

```perl

print scalar grep { $_ eq "Columbus" } @capitals; # "1"
```

`grep`和`map`的组合形成了_list comprehensions_这种许多其他语言中欠缺的非常强大特性。（译者注：list comprehensions大致的意思是利用map和filter从现有的列表构造新的列表，表达的含义是对一个列表中满足某个条件的所有元素上应用某个操作，而形成一个新的列表。）

默认情况下，`sort`函数对输入的array按字母序进行排序：

```perl

my @elevations = (19, 1, 2, 100, 3, 98, 100, 1056);

print join ", ", sort @elevations;
# "1, 100, 100, 1056, 19, 2, 3, 98"
#根据内部的字符编码进行顺序 进行排序；
```

然而，与`grep`和`map`类似，排序总是通过一系列元素的两两比较来进行的。你的代码块接受`$a`和`$b`作为输入，如果`$a`“小于”`$b`则返回-1，如果“相等”则返回0，而如果`$a`“大于”`$b`则返回1。

`cmp`运算符适用于字符串（译者注：按字母序比较）：

```perl

print join ", ", sort { $a cmp $b } @elevations;
# "1, 100, 100, 1056, 19, 2, 3, 98"
```

这个“宇宙飞船运算符”`<=>`适用于数值：

```perl

print join ", ", sort { $a <=> $b } @elevations;
# "1, 2, 3, 19, 98, 100, 100, 1056"
```

`$a`和`$b`总是scalar，但是它们也许是某个复杂对象的引用，那样就很难直接进行比较。如果你需要更多篇幅来描述这种比较，你可以单独创建一个子程序来描述它，并在用到它的地方提供这个子程序的名字：

```perl

sub comparator {
# lots of code...
# return -1, 0 or 1
}

print join ", ", sort comparator @elevations;
```

不过你不能对`grep`或`map`这样做。

请注意，我们从来没有显式提供`$a`和`$b`给子程序和语句块。就像`$_`一样，`$a`和`$b`实际上是当一对值需要比较时被_填入_的全局变量。