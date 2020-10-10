---
title: perl syntax 0
tags:
  - perl
  - Shell
id: '296'
categories:
  - - programming
    - Perl
  - - 程序人生
date: 2017-08-10 17:12:25
---

```perl

#! /usr/bin/perl

use warnings;
use diagnostics;
# 1.编译指示，给perl的一个提示，在程序开始之前的语法验证阶段会发挥作用，
# 脚本语句实际执行的时候，对运行结果没有影响
use utf8;
require 5.22.2;
#2.变量 共有三类：标量（scalar）、数组（array）、哈希（hashes）
#2.1 Scalar variables
$what = "your name";
$n = 3;
print "what is $what ?\n";
print "what is ${what}s $n?\n";

# others 特殊符号
$alef = chr(0x05D0);
$alpha = chr(hex('03B1'));
$omega = chr(0x03C9);

print "$alef,";
print "$alpha,";
print "$omega \n";

#booleans perl 没有内置布尔类型。if语句中，scalar变量仅在一下情况被认为是“false”
#undef
#数值 0
#字符串 ””
#字符串 “0”
my $undef = undef;
print $undef,"\n";
#弱类型
#无法判定一个scalar包含的是一个数值还是字符串。
#因为这完全是取决于 运算符的。
my $str1 = "4G";
my $str2 = "4H";

print $str1 .  $str2,"\n"; # "4G4H"
print $str1 +  $str2,"\n"; # "8" 并且抛出两个警告
print $str1 eq $str2,"\n"; # "" （空字符串，也就是false）
print $str1 == $str2,"\n"; # "1" 并且抛出两个警告

# 经典错误
print "yes" == "no"; # "1" 并且抛出两个警告，按数值方式参与运算，两边求值结果都是0

# 在恰当的情况下使用正确的运算符，对于比较数值和字符串有两套不同的运算符：
# 数值运算符：  <,  >, <=, >=, ==, !=, <=>, +, *
# 字符串运算符：    lt, gt, le, ge, eq, ne, cmp, ., x

#2.2 array variables
# Array变量是包含一个scalar列表的、由从0开始的整形数为下标存取的变量。
# 在Python里被称为list，而在PHP里被称为array。数组可以用一个圆括号包围的scalar列表来声明
my @array = (
"print",
"these",
"string",
"out",
"for",
"me"
);
for (my $var = 0; $var < 7; $var++) {
print $array[$var]," ";
}
print "\n";

#length of array
print "this array has ".(scalar @array)."  elements \n";
print "The last populated index is ".$#array."\n";

# reverse output
for (my $var = -1; $var >=-7; $var--) {
print $array[$var]," ";
# body...
}
print "\n";

# 当@当做邮箱地址使用时，要注意进行转义，或者将双引号改为单引号
print "Hello \$string","\n"; # "Hello $string"
print 'Hello $string',"\n";  # "Hello $string"
print "\@array","\n";        # "@array"
print '@array',"\n";         # "@array"

#hash variables

my %architecture = (
"Tesla"   => "first  generation",
"Fermi"   => "second generation",
"Kepler"  => "third  generation",
"Maxwell" => "fourth generation",
"Pascal"  => "fifth  generation",
);
print "Fermi is ".$architecture{"Fermi"}." of Nvidia GPU architecture !\n";

#You can convert a hash straight to an array with twice as many entries, alternating between key and value
my @architecture = %architecture;
print "@architecture \n";

#use square brackets to retrieve a value from an array, but you have to use braces to retrieve a value from a hash.
my $data = "orange";
my @data = ("purple");
my %data = ( "0" => "blue");

print $data," 1 \n";      # "orange"
print $data[0]," 2 \n";   # "purple"
print $data["0"]," 3 \n"; # "purple"
print $data{0}," 4 \n";   # "blue"
print $data{"0"}," 5 \n"; # "blue"
print "hello perl !\n";

#list
#列表不是一个变量，只是一个暂存的值，可以被赋值到一个array或者哈市变量中。
#这就是为什么array和hash的语法竟然完全一样的原因了。
# => 只是 .  的伪装
#列表不能嵌套，perl将其扁平化为一个 一维列表
(
"print",
"these",
"strings",
"out",
"for",
"me",
);
(

"Newton"   => "Isaac",
"Einstein" => "Albert",
"Darwin"   => "Charles",
);
```

END