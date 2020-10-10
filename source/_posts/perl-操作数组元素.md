---
title: Perl 操作数组元素
tags:
  - perl
id: '306'
categories:
  - - programming
    - Perl
  - - 程序人生
date: 2017-08-11 08:50:00
---

# 操作Perl数组

和可以直接访问单独的数组元素一样，Perl也提供了很多其它有趣的方式来操作数组。特别是，有些函数可以很方便有效的将Perl的数组作为栈或者队列来使用。

### pop

`pop`函数会删除并返回数组的最后一个元素。

在第一个例子（3元素数组）中可以看到，`pop`函数删除最后一个元素（下标最大）并返回它。

```perl

my @names = ('Foo', 'Bar', 'Baz');

my $last_one = pop @names;

print "$last_one\n";  # Baz

print "@names\n";     # Foo Bar
```

如果原数组为空，pop函数会返回undef。

### push

`push`函数可以在数组的后面添加一个或多个值。(当然，也可以添加0个值，但是没有用，不是么？)

```perl

my @names = ('Foo', 'Bar');

push @names, 'Moo';

print "@names\n";     # Foo Bar Moo

my @others = ('Darth', 'Vader');

push @names, @others;

print "@names\n";     # Foo Bar Moo Darth Vader
```

在这个例子中我们最初有个两元素数组。之后我们向数组尾部push了一个标量，数组扩展成了3元素数组。

第二次调用`push`，我们`push`了`@others`数组的内容到`@names`尾部，把它扩充成5元素数组。

### shift

shift函数会让整个数组左移。设想一下，数组从左边开始。数组的第一个元素会从数组“掉下来”，并成为函数的返回值(如果数组为空，`shift` 会返回 `undef`。)

这样操作之后，数组会减少一个元素。

```perl

my @names = ('Foo', 'Bar', 'Moo');

my $first = shift @names;

print "$first\n";     # Foo

print "@names\n";     # Bar Moo
```

这和`pop`很像，但是它作用于数组索引的小端。

### unshift

这是`shift`的反函数。`unshift` 会传入一个或多个值(或者0个) 并把它放在数组的开头，将其他元素右移动。

你可以向它传单个的标量，那么这个值会成为数组的第一个元素。或者像第二个例子那样，你可以传递第二个数组，那么第二个数组的所有元素(我们例中的`@others`)会复制到主数组的开头(例中`@names`)，并将其他元素向高索引方向移动。

```perl

my @names = ('Foo', 'Bar');

unshift @names, 'Moo';

print "@names\n";     # Moo Foo Bar

my @others = ('Darth', 'Vader');

unshift @names, @others;

print "@names\n";     # Darth Vader Moo Foo Bar
```