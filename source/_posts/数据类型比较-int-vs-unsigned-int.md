---
title: 数据类型比较 int vs unsigned int
tags: []
id: '1262'
categories:
  - - programming
    - C/C++
comments: false
date: 2020-05-04 12:10:57
---

起因是 云智能的安全考试有一题，如下图所示：

![compare-int-uint.png](https://intranetproxy.alipay.com/skylark/lark/0/2020/png/131289/1583462428201-988e2be3-f143-43df-b4f1-a0102482ff84.png "compare-int-uint.png")

*   这个题涉及的就是不同类型数据，如何进行比较
*   如果是个数学题，a>b,a<c; 则 b>c 肯定是错的了。。
*   按照选择题思路，AD至少选一个。。没看D选项GG；

言归正传，先写了一段小代码看看。

#include <stdio.h>
#include <stdlib.h>

int main() {
  int a;
  int b;
  unsigned int c;

  a = 0;
  b = 0xffffffff;
  c = 0x80000000;

  printf(" cout in int\\n");
  printf(" a = %d \\n", (a));
  printf(" b = %d \\n", (b));
  printf(" c = %d \\n", (c));

  printf(" cout in unsigned int\\n");
  printf(" a = %u \\n", (a));
  printf(" b = %u \\n", (b));
  printf(" c = %u \\n", (c));

  printf(" a>b ? = %d \\n", (a>b));
  printf(" a<c ? = %d \\n", (a<c));
  printf(" b>c ? = %d \\n", (b>c));
  printf(" a<b ? = %d \\n", (a<b));
  return 0;
}

看看运行结果是啥？

![image.png](https://intranetproxy.alipay.com/skylark/lark/0/2020/png/131289/1583462724897-97ddd17b-385c-4476-a1cb-ee84252c8d07.png "image.png")

好吧，选D是正确的，但是为啥呢？

分析一下：

首先 a 跟 b 进行比较，同为int类型，不必做类型转换：

*   `0>-1`  这个可以理解；
*   看一下内存表示
*   `0x00000000 vs 0xffffffff` 

第二 a 跟 c 进行比较，a 为 int 类型，c 为 unsigned int 类型

这个问题就需要说道一下了

*   如果 将 c 转换为 int 类型，那么 c 就变为一个 负数，显然 a = 0 > c, 那么合理吗？显然不合理。。
*   unsigned int 的语义就是无符号整数，永远是 >= 0 的，因此 两者比较时，int 会 转换为 unsigned int；
*   因此 (a=0) < (c= 2147483648)

第三 b 跟 c 进行比较

*   也是 int vs unsigned int
*   转化为 unsigned int
*   `0xffffffff > 0x80000000` 
*   其实我在语义上是存在疑惑的，但如果放到内存上，无关类型进行比较的话，那么必然是 0xffffffff 大于 0x80000000；

> [https://stackoverflow.com/questions/8233161/compare-int-and-unsigned-int](https://stackoverflow.com/questions/8233161/compare-int-and-unsigned-int)

看到 stackoverflow 的 这个比较还是更合理一些的：

if (x >= 0 && ((unsigned int)x) == y)