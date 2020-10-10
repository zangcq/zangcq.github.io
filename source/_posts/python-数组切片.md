---
title: Python 数组切片
tags: []
id: '1003'
categories:
  - - programming
    - Python
comments: false
date: 2019-10-29 15:11:07
---

##### 1/循环

取前N个元素，也就是索引为0-(N-1)的元素，可以用循环：

```
r = []
n = 3
for i in range(n):
...     r.append(L[i])
... 
r
['Michael', 'Sarah', 'Tracy']
```

##### 2/切片符 ：（冒号）

*   规则 Slicing is specified using the colon operator ‘:’ with a ‘from‘ and ‘to‘ index before and after the column respectively. The slice extends from **the ‘from’ index** and **ends one item before the ‘to’ index**.
*   冒号
*   `data[from:to]`
*   从from index元素开始 到 to的前一个元素为止。
*   default 为`0:len(x)`
*   对应上面的问题，取前3个元素，用一行代码就可以完成切片：举例说明

```
L[0:3]
['Michael', 'Sarah', 'Tracy']
L[0:3]表示，从索引0开始取，直到索引3为止，但不包括索引3。即索引0，1，2，正好是3个元素。
```

*   默认从零开始索引，一些例子

```
  # 如果第一个索引是0，还可以省略：
  # 从0，1，2；3不包括
  L[:3]
  ['Michael', 'Sarah', 'Tracy']

  # 也可以从索引1开始，取出2个元素出来：
  # 1，2
  L[1:3]
  ['Sarah', 'Tracy']

  # 类似的，既然Python支持L[-1]取倒数第一个元素，那么它同样支持倒数切片，试试：
  # -2，-1 到最后一个，负号代表倒着数
  L[-2:]
  ['Bob', 'Jack']
  # -1不包括，只有倒数第二个
  L[-2:-1]
  ['Bob']
```

**记住倒数第一个元素的索引是-1**。

*   切片操作十分有用。

```
  # 创建一个0-99的数列：
  L = list(range(100))
  L
  [0, 1, 2, 3, ..., 99]

  # 可以通过切片轻松取出某一段数列。比如前10个数：
  L[:10]
  [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

  # 后10个数：
  L[-10:]
  [90, 91, 92, 93, 94, 95, 96, 97, 98, 99]

  # 前11-20个数：
  L[10:20]
  [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]

  #前10个数，每两个取一个：
  # 第一个冒号后边表示从所有数中取数字
  # 第二个冒号的含义，是对此 取余 的对应index的数
  L[:10:2]
  [0, 2, 4, 6, 8]

  # 所有数，每5个取一个：
  L[::5]
  [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95]

  # 甚至什么都不写，只写[:]就可以原样复制一个list：
  L[:]
  [0, 1, 2, 3, ..., 99]

  # tuple也是一种list，唯一区别是tuple不可变。因此，tuple也可以用切片操作，只是操作的结果仍是tuple：
  (0, 1, 2, 3, 4, 5)[:3]
  (0, 1, 2)
  # 字符串'xxx'也可以看成是一种list，每个元素就是一个字符。
  # 因此，字符串也可以用切片操作，只是操作结果仍是字符串：

  'ABCDEFG'[:3]
  'ABC'
  'ABCDEFG'[::2]
  'ACEG'
```

在很多编程语言中，针对字符串提供了很多各种截取函数（例如，substring），其实目的就是对字符串切片。Python没有针对字符串的截取函数，只需要切片一个操作就可以完成，非常简单。

*   **多维切片**，将不变的维度固定，切片时按照一维切片进行

```
  # split train and test
  from numpy import array
  # define array
  data = array([[11, 22, 33],
          [44, 55, 66],
          [77, 88, 99]])
  # separate data
  split = 2
  train,test = data[:split,:],data[split:,:]
  print(train)
  print(test)
```

结果

```
  # train [0,split-1 ]行
  [[11 22 33]
  [44 55 66]]
  # test [split，len（x）-1] 行
  [[77 88 99]]

  列方向同理
```

##### 3/ 没有冒号

*   数字即当做索引来处理，每一维度数量当做1，index即为对应数字

```
# split input and output
from numpy import array
# define array
data = array([[11, 22, 33],
        [44, 55, 66],
        [77, 88, 99]])
# separate data
X, y = data[:, :-1], data[:, -1]
print(X)
print(y)
```

*   结果

```
# X  行不动，从列方向上切
[[11 22]
 [44 55]
 [77 88]]
# y ，直接为索引，序号-1，即最后一列
[33 
 66 
 99]
```

##### Reference

> https://www.liaoxuefeng.com/wiki/1016959663602400/1017269965565856#0
> 
> https://machinelearningmastery.com/index-slice-reshape-numpy-arrays-machine-learning-python/