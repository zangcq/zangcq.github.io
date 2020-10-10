---
title: 代码质量保证工具 valgrind
tags: []
id: '644'
categories:
  - - 工欲善其事必先利其器
date: 2018-09-03 21:17:38
---

## overview

Valgrind是一款用于内存调试、内存泄漏检测以及性能分析的软件开发工具。

其包含的工具主要有Memcheck，Cachegrind，Callgrind，Massif等。其中，最为常用的是Memcheck，其主要用来检查程序上的内存情况。

> [http://valgrind.org/](http://valgrind.org/)

可用的工具

*   cachegrid
    
    缓存模拟器，用来标出程序每一条指令和导致的缓存miss 数
    
*   callgrind
    
    在cachegrind基础上添加的调用追踪，可以得到函数调用次数和开销。
    
*   helgrind
    
    发现程序中潜在的条件竞争
    
*   lackey
    
    示例程序，作为模板创建自己的工具
    
*   **memcheck**
    
    Memcheck is a memory error detector. It can detect the following problems that are common in C and C++ programs.
    
    *   **Accessing memory you shouldn't**, e.g. overrunning and underrunning heap blocks, overrunning the top of the stack, and accessing memory after it has been freed.
        
        非法访问，如读写已经被释放的内存
        
    *   **Using undefined values**, i.e. values that have not been initialised, or that have been derived from other undefined values.
        
        使用未定义（为初始化的）值
        
    *   **Incorrect freeing of heap memory**, such as double-freeing heap blocks, or mismatched use of `malloc`/`new`/`new[]` versus `free`/`delete`/`delete[]`
        
        分配与释放不匹配
        
    *   **Overlapping `src` and `dst` pointers** in `memcpy` and related functions.
        
        源指针与目的指针重叠
        
    *   Passing a fishy (presumably negative) value to the `size` parameter of a memory allocation function.
        
    *   **Memory leaks**.
        
        内存泄漏
        

![](http://www.zangcq.com/wp-content/uploads/2018/09/Memcheck-error-message-Explanation.png)

### Memory leak detection

#### interior-pointer

*   The pointer might have originally been a start-pointer and have been moved along deliberately (or not deliberately) by the program. In particular, this can happen if your program uses tagged pointers, i.e. if it uses the bottom one, two or three bits of a pointer, which are normally always zero due to alignment, in order to store extra information.
*   It might be a random junk value in memory, entirely unrelated, just a coincidence.
*   It might be a pointer to the inner char array of a C++ `std::string`. For example, some compilers add 3 words at the beginning of the std::string to store the length, the capacity and a reference count before the memory containing the array of characters. They return a pointer just after these 3 words, pointing at the char array.
*   Some code might allocate a block of memory, and use the first 8 bytes to store (block size - 8) as a 64bit number. `sqlite3MemMalloc` does this.
*   It might be a pointer to an array of C++ objects (which possess destructors) allocated with `new[]`. In this case, some compilers store a "magic cookie" containing the array length at the start of the allocated block, and return a pointer to just past that magic cookie, i.e. an interior-pointer. See [this page](http://theory.uwinnipeg.ca/gnu/gcc/gxxint_14.html) for more information.
*   It might be a pointer to an inner part of a C++ object using multiple inheritance.

#### Pointor cases

With that in mind, consider the nine possible cases described by the following figure.

```c
     Pointer chain            AAA Leak Case   BBB Leak Case
     -------------            -------------   -------------
(1)  RRR ------------> BBB                    DR
(2)  RRR ---> AAA ---> BBB    DR              IR
(3)  RRR               BBB                    DL
(4)  RRR      AAA ---> BBB    DL              IL
(5)  RRR ------?-----> BBB                    (y)DR, (n)DL
(6)  RRR ---> AAA -?-> BBB    DR              (y)IR, (n)DL
(7)  RRR -?-> AAA ---> BBB    (y)DR, (n)DL    (y)IR, (n)IL
(8)  RRR -?-> AAA -?-> BBB    (y)DR, (n)DL    (y,y)IR, (n,y)IL, (_,n)DL
(9)  RRR      AAA -?-> BBB    DL              (y)IL, (n)DL

Pointer chain legend:
- RRR: a root set node or DR block
- AAA, BBB: heap blocks
- --->: a start-pointer
- -?->: an interior-pointer

Leak Case legend:
- DR: Directly reachable
- IR: Indirectly reachable
- DL: Directly lost
- IL: Indirectly lost
- (y)XY: it's XY if the interior-pointer is a real pointer
- (n)XY: it's XY if the interior-pointer is not a real pointer
- (_)XY: it's XY in either case
```

#### Leak Message Case

Every possible case can be reduced to one of the above nine. Memcheck merges some of these cases in its output, resulting in the following four leak kinds.

*   "**Still reachable**". This covers **cases 1 and 2** (for the BBB blocks) above. A start-pointer or chain of start-pointers to the block is found. Since the block is still pointed at, the programmer could, at least in principle, have freed it before program exit. **"Still reachable" blocks are very common and arguably not a problem.** So, by default, Memcheck won't report such blocks individually.
*   "**Definitely lost**". This covers **case 3** (for the BBB blocks) above. This means that no pointer to the block can be found. The block is classified as "lost", because the programmer could not possibly have freed it at program exit, since no pointer to it exists. This is likely a symptom of having lost the pointer at some earlier point in the program. Such cases should be fixed by the programmer.
*   "**Indirectly lost**". This covers **cases 4 and 9** (for the BBB blocks) above. This means that the block is lost, not because there are no pointers to it, but rather because all the blocks that point to it are themselves lost. For example, if you have a binary tree and the root node is lost, all its children nodes will be indirectly lost. Because the problem will disappear if the definitely lost block that caused the indirect leak is fixed, Memcheck won't report such blocks individually by default.
*   "**Possibly lost**". This covers **cases 5--8** (for the BBB blocks) above. This means that a chain of one or more pointers to the block has been found, but at least one of the pointers is an interior-pointer. This could just be a random value in memory that happens to point into a block, and so you shouldn't consider this ok unless you know you have interior-pointers.