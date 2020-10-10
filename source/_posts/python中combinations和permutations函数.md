---
title: python中combinations和permutations函数
tags: []
id: '839'
categories:
  - - programming
    - Python
date: 2019-06-11 16:47:50
---

#### 说明

*   combinations方法在**组合**
*   permutations方法在**排列**
*   python2中返回list

#### eg

```
 zangchuanqideMacBook-Pro:zcq$ python
 Python 2.7.16 (default, Apr  1 2019, 14:50:41)
 [GCC 4.2.1 Compatible Apple LLVM 10.0.1 (clang-1001.0.46.3)] on darwin
 Type "help", "copyright", "credits" or "license" for more information.
 >>> import itertools
 >>> list1=list(itertools.combinations('abc',2))
 >>> print list1
 [('a', 'b'), ('a', 'c'), ('b', 'c')]
 >>> list2=list(itertools.permutations('abc',2))
 >>> print list2
 [('a', 'b'), ('a', 'c'), ('b', 'a'), ('b', 'c'), ('c', 'a'), ('c', 'b')]
```