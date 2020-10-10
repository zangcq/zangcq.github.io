---
title: PTX ISA 之 同步指令
tags: []
id: '26'
categories:
  - - gpu-computing
    - GPU PTX ISA Analysis
date: 2017-06-06 14:41:30
---

# PTX ISA---同步指令

## bar

#### bar

Barrier synchronization.

#### Syntax

```c

bar.sync     a{, b};//  __synthread();
bar.arrive   a, b;
// a 表示 barrier 的编号 0到15
// b 表示 线程的数量，如果b没确定，默认是cta 所有的线程

bar.red.popc.u32   d, a{, b}, {!}c;

bar.red.op.pred    p, a{, b}, {!}c;
//Once the barrier count is reached, the final value is written to the destination register in all threads waiting at the barrier.
.op = { .and, .or };
```

#### Description

​ Performs barrier synchronization and communication within a CTA. Each CTA instance has sixteen barriers numbered 0..15 . 每个 cta 有16个 barrier ，从 0 到15. the **bar.sync and bar.red** instructions cause the executing thread to wait until all or a specified number of threads in the CTA arrive at the barrier before resuming execution. 上边两条指令，使正在执行的 线程 等待 直到 CTA 所有线程 到达barrier ，才能继续执行。 **bar.red** performs a predicate reduction across the threads participating in the barrier. bar.red 通过线程s 分享 barrier 实现了一个 谓语的规约么》？？ **bar.arrive** does not cause any waiting by the executing threads; it simply marks a thread's arrival at the barrier. bar.arrive 不会造成对 正在执行的线程 任何等待；它只是在想成到达的时候简单的标记一下。

#### example

```c

// Use bar.sync to arrive at a pre-computed barrier number and
// wait for all threads in CTA to also arrive:
st.shared [r0],r1; // write my result to shared memory
bar.sync 1;// arrive, wait for others to arrive
ld.shared r2,[r3]; // use shared results from other threads

// Use bar.sync to arrive at a pre-computed barrier number and
// wait for fixed number of cooperating threads to arrive:
#define CNT1 (8*12) // Number of cooperating threads
st.shared [r0],r1;// write my result to shared memory
bar.sync 1, CNT1;// arrive, wait for others to arrive
ld.shared r2,[r3];// use shared results from other threads

// Use bar.red.and to compare results across the entire CTA:
setp.eq.u32 p,r1,r2;// p is True if r1==r2
bar.red.and.pred r3,1,p; // r3=AND(p) forall threads in CTA

// Use bar.red.popc to compute the size of a group of threads
// that have a specific condition True:
setp.eq.u32 p,r1,r2;// p is True if r1==r2
bar.red.popc.u32 r3,1,p; // r3=SUM(p) forall threads in CTA

/* Producer/consumer model. The producer deposits a value in
* shared memory, signals that it is complete but does not wait
* using bar.arrive, and begins fetching more data from memory.
* Once the data returns from memory, the producer must wait
* until the consumer signals that it has read the value from
* the shared memory location. In the meantime, a consumer
* thread waits until the data is stored by the producer, reads
* it, and then signals that it is done (without waiting).
*/
// Producer code places produced value in shared memory.
st.shared
[r0],r1;
bar.arrive 0,64;
ld.global
r1,[r2];
bar.sync
1,64;
...
// Consumer code, reads value from shared memory
bar.sync
0,64;
ld.shared r1,[r0];
bar.arri
```

## membar

Memory barrier.

#### Syntax

```c

membar.level;

.level = { .cta, ,gl, ,sys };
```

#### Description

Waits for all prior memory accesses requested by this thread to be performed at the CTA, global, or system memory level. 等待所有之前的访存请求，来自 CTA ，global，系统存储级的 Thread execution resumes after a membar when the thread's prior memory writes are visible to other threads at the specified level , and memory reads by this thread can no longer be affected by other thread writes. 线程重新执行 在一个 membar 之后，当这个线程之前的写操作对其他线程可见的时候（在特定的范围），并且这个线程的读操作，不再受其他线程写的影响。 A **memory read** (e.g., by ld or atom ) has been performed when the value read has been transmitted from memory and cannot be modified by another thread at the indicated level. 当这个要读的值不会被其他线程修改时，这个读请求才会执行。 A **memory write** (e.g., by st , red or atom ) has been performed when the value written has become visible to other clients at the specified level, that is, when the previous value can no longer be read. 当这个要被写的值 对于其他 clien 可见，之前的值不会再被读了，的时候，这个写操作才会执行。

#### **membar.cta**

Waits until all prior memory writes are visible to other threads in the same CTA. 等待所有之前的写操作对，，所有在CTA里其他线程可见。 Waits until prior memory reads have been performed with respect to other threads in the CTA. 等待，所有之前的读操作，涉及到在CTA里的其他线程都已经完成。

#### **membar.gl**

Waits until all prior memory requests have been performed with respect to all other threads in the GPU. 等待，直到所有之前涉及GPU里的其他线程的访存请求都已经完成 For communication between threads in different CTAs or even different SMs, this is the appropriate level of membar. 这个是为了 在 不同CTA 甚至不同 SMs 之间的 交流，专属的级别的 membar。 SM 或者说是 inter-workgroup block 之间的 同步吧。 membar.gl will typically have a longer latency than membar.cta . gl要比cta 的延时长一些。

#### **membar.sys**

Waits until all prior memory requests have been performed with respect to all clients, including thoses communicating via PCI-E such as system and peer-to-peer memory. 等待，直到所有的涉及 所有 client ？？访存请求 都 完成。 包括 主存跟显存通过 PCI-E来交流。 相当于 CPU 跟 GPU之间的同步吧？？ This level of membar is required to insure performance with respect to a host CPU or other PCI-E peers. **membar.sys** will typically have much longer latency than **membar.gl** . 这个延时更长