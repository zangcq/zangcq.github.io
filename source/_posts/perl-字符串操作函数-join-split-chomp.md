---
title: Perl 字符串操作函数　join split chomp
tags:
  - perl
id: '310'
categories:
  - - programming
    - Perl
  - - 程序人生
date: 2017-08-11 08:59:55
---

# Perl 字符串操作函数　join split chomp

## join 函数

将字符串列表，用分隔符连接起来，生成一个更长的字符串。

### 语法

```perl

join EXPR, LIST
//expr 就是用于连接的分隔符
//list 就是字符串列表
```

### 例子

```perl

$string = join( "-", "one", "two", "three" );
print"Joined String is $string\n";

$string = join( "", "one", "two", "three" );
print"Joined String is $string\n";
#result
#Joined String is one-two-three
#Joined String is onetwothree
```

## split 函数

将一个字符串，通过分隔符，最后生成有许多子串的数组或者列表。

### 语法

```perl

split /PATTERN/,EXPR,LIMIT
split /PATTERN/,EXPR
split /PATTERN/
split
```

### 例子

```perl

@fields = split(/:/, "1:2:3:4:5");
print "Field values are: @fields\n";
#result
#Field values are: 1 2 3 4 5
```

## chomp

### 语法

```perl

chomp VARIABLE
chomp( LIST )
```

```perl

chomp 是 chop 的安全版本，相对于chop 删除字符串或list最后任意字符。
chomp 只删除 '\n',否则不删除。
```

### VARIABLE == string

```perl

例1：$str="test function of chomp\n";
    chomp($str);#去掉结尾的\n

例2：$str=<STDIN>;#从标准输入中读入
     chomp($str);

上面的二行可以合并为chomp($str=<STDIN>)

例3.$test="string";
    chop $test;
    print $test;#结尾的g将被去掉

备注：
1.在使用chomp的时候，可以不使用圆括号()，即chomp $str;
2.如果字符串结尾有2个或2个以上的换行符\n，chomp只去掉一个。
3.如果字符串结尾没有换行符，那chomp什么都不做，返回0。

```

### VARIABLE == hash

```perl

If VARIABLE is a hash, it chomps the hash's values, 
but not its keys, resetting the each iterator in the process
```

### VARIABLE == list

```perl

If you chomp a list, each element is chomped, 
and the total number of characters removed is returned.
```

```perl

    while (<>) {
        chomp;  # avoid \n on last field
        my @array = split(/:/);
        # ...
    }
```

### chop和chomp函数区别

```perl

chop函数负责删除标量型标量的最后一个字符或数组中每个元素的最后一个字符，并返回修改后的值。
chop一般用于删除程序接收到的输入行末尾的换行符，这些输入行可以来自STDIN、文件或者命令置换结果。

chomp函数，负责删除标量型变量中的最后一个字符，或者数组中每个字的最后一个字符，
并保证只有该行末字符是换行符时才进行删除操作。它会返回删除后的字符数目。
使用chomp函数来代替chop，能避免删除换行符之外的其它字符。
```