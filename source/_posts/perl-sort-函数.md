---
title: perl sort 函数
tags:
  - perl
id: '308'
categories:
  - - programming
    - Perl
  - - 程序人生
date: 2017-08-11 08:51:32
---

## perl sort 函数

`sort` 为内置函数，可以对数组进行排序。其最简单的形式是传递一个数组，他会返回排序后的数组。

默认是基于`ASCII`码由小到大排序。

eg

`@list = sort @orginal`

### 语法

```perl

sort subname list
sort block  list
sort list
```

### 默认排序

eg

```perl

#!/usr/bin/perl

use strict;

use warnings;

use 5.010;

use Data::Dumper qw(Dumper);

my @words = qw(foo bar zorg moo);

say Dumper \@words;

my @sorted_words = sort @words;

say Dumper \@sorted_words;
```

上边的例子将会打印

```perl

 $VAR1 = [
    'foo',
    'bar',
    'zorg',
    'moo'
  ];
```

```perl

 $VAR1 = [  
    'bar',
    'foo',
    'moo',
    'zorg'
  ];
```

第一个输出显示了排序前的数组，第二个是排序后的。

这是最简单的情形，但是可能未必是你想要的。 比如，如果一些单词以大写字母开头怎么办？

`my @words = qw(foo bar Zorg moo);` `@sorted_names`里的结果将是：

```perl

  $VAR1 = [
    'Zorg',
    'bar',
    'foo',
    'moo'
  ];
```

你会发现，以大写字母开头的单词排在了第一位。 这是因为sort默认根据ASCII码表排序，所有的大写字母都排在小写字母前边。

### 比较函数

`Perl`的`sort`的工作方式是这样的，它遍历原始数组的每两个元素；每次把左边的值放入变量`$a`，把右边的值放入变量`$b`。 然后调用比较函数。如果`$a`的内容应该在左边的话，“比较函数”会返回1；如果`$b`应该在左边的话，返回-1，两者一样的话，返回0。

通常你看不到比较函数，sort会根据ASCII码表对值进行比较，不过如果你想的话，你可以显式的写出来：

`sort { $a cmp $b } @words;` 这段代码会跟没有使用块的`sort @words`达到同样的效果。

这里你可以看到，默认`perl`使用`cmp`作为比较函数。这是因为正是`cmp`可以做这里边我们需要的工作。 它比较两边的字符串的值，如果左边参数“小于”右边参数，就返回1；如果左边参数“大于”右边参数，就返回-1；如果相等，就返回0。

按字母顺序排列 如果你想忽略字符串的大小写来排序——即通常所谓的字母序，你可以像下一个例子这么做：

`my @sorted_words = sort { lc($a) cmp lc($b) } @words;` 这里为了比较，我们调用lc函数返回参数的小写版本。然后cmp比较这些小写版本并决定原始字符串谁先谁后。

结果是

```perl

 $VAR1 = [
    'bar',
    'foo',
    'moo',
    'Zorg'
  ];
```

### Perl对数值排序

如果对数值数组使用`sort`进行默认的排序，结果可能不是我们期望的。

```perl

my @numbers = (14, 3, 12, 2, 23);

my @sorted_numbers = sort @numbers;

say Dumper \@sorted_numbers;
```

```perl

  $VAR1 = [
    12,
    14,
    2,
    23,
    3
  ];
```

仔细一想的话，这并不奇怪。比较函数看到12和3时，它按字符串进行比较。这意味着比较两个字符串的第一个字符"1"和"3"。 在`ASCII`码表里，"1"在"3"前边，因此字符串"12"会排在字符串"3"前面。

`Perl`不会很神奇地猜到你想按数字对这些值排序。

尽管我们可以写一个比较函数来按数字比较两个值。但这里我们使用`<=>`（也被称作宇宙飞船操作符）， 它会按数字来比较两个参数并返回1、-1或者0。

`my @sorted_numbers = sort { $a <=> $b } @numbers;` 结果是：

```perl

   $VAR1 = [
    2,
    3,
    12,
    14,
    23
  ];
```