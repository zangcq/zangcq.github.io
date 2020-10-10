---
title: PTX ISA special-registers
tags:
  - GPU
  - PTX ISA
id: '313'
categories:
  - - gpu-computing
    - GPU PTX ISA Analysis
date: 2017-08-11 14:31:52
---

# PTX ISA [Special Registers](http://docs.nvidia.com/cuda/parallel-thread-execution/index.html#special-registers)

## 综述

PTX includes a number of predefined, read-only variables, which are visible as special registers and accessed through mov or cvt instructions.

*   `%tid` 　　　　　  
    
    *   CTA 内的线程号　
*   `%ntid`　　　　　　
    
    *   CTA 内的线程数　
*   `%laneid`　　　　　
    
    *   warp内的线程号
*   `%warpid`　　　　　
    
    *   CTA 内的warp号
*   `%nwarpid`　　　　  
    
    *   CTA 内的warp数　
*   `%ctaid` 　　  
    
    *   CTA 号　
*   `%nctaid`　　　　　  
    
    *   CTA 数　
*   `%smid`　　　　　　
    
    *   SM 号
*   `%nsmid`　　　　　  
    
    *   SM数
*   `%gridid`　　　　　  
    
    *   网格号　包含　多个ＣＴＡ
*   `%lanemask_eq, %lanemask_le, %lanemask_lt, %lanemask_ge, %lanemask_gt`
    
    *   从fermi架构开始提出的线程掩码寄存器，大小32位，我表示每个warp中　active 的线程数。
    *   不大常见
*   `%clock, %clock_hi, %clock64`
    
    *   无符号预定义只读的 计数寄存器
    *   %clock　　　　　 32位
    *   %clock\_hi　　　高32位
    *   %clock64　　　　 64位
*   `%pm0, ..., %pm7`
    
    *   performance monitoring　counters
    *   性能监视计数器，没用过。。
*   `%pm0_64, ..., %pm7_64`
    
    *   \`\`64 bit performance monitoring　counters
    *   性能监视计数器，没用过。。
*   `%envreg0, ..., %envreg31`
    
    *   Driver-defined read-only registers.
    *   驱动器只读寄存器
    *   用来获取PTX程序运行环境，ARCH?
*   `%globaltimer, %globaltimer_lo, %globaltimer_hi`
    
    *   A predefined, 64-bit global nanosecond timer.
    *   全局纳秒寄存器
    *   64 bit low 32 bit high 32 bit
*   `%total_smem_size` 　　　　
    
    *   每个CTA使用shared memory 的大小　举个例子　fermi 16K/32K
*   `%dynamic_smem_size`　　  
    
    *   这个是kernel 函数启动时动态分批的总大小

看完综述应该大体上知道这些都是干嘛的了，如果还想详细了解，再往下看。

## 9.1. Special Registers: %tid

`%tid` ​Thread identifier within a CTA.

### Syntax (predefined)

`.sreg .v4 .u32 %tid; // thread id vector` `.sreg .u32 %tid.x, %tid.y, %tid.z; // thread id components`

### Description

A predefined, read-only, per-thread special register initialized with the thread identifier within the CTA. The `%tid` special register contains a 1D, 2D, or 3D vector to match the CTA shape; the `%tid` value in unused dimensions is `0`. The fourth element is unused and always returns zero. The number of threads in each dimension are specified by the predefined special register `%ntid`.

Every thread in the CTA has a unique `%tid`.

`%tid` component values range `from 0 through %ntid-1` in each CTA dimension.

`%tid.y == %tid.z == 0 in 1D CTAs. %tid.z == 0 in 2D CTAs.`

It is guaranteed that:

`0 <= %tid.x < %ntid.x` `0 <= %tid.y < %ntid.y` `0 <= %tid.z < %ntid.z`

### PTX ISA Notes

Introduced in PTX ISA version 1.0 with type .v4.u16.

Redefined as type .v4.u32 in PTX ISA version 2.0. For compatibility with legacy PTX code, 16-bit mov and cvt instructions may be used to read the lower 16-bits of each component of %tid.

### Target ISA Notes

Supported on all target architectures.

### Examples

```c++

mov.u32      %r1,%tid.x;  // move tid.x to %rh
// legacy code accessing 16-bit components of %tid
mov.u16      %rh,%tid.x;
cvt.u32.u16  %r2,%tid.z;  // zero-extend tid.z to %r2
```

## 9.2. Special Registers: %ntid

`%ntid` Number of thread IDs per CTA.

### Syntax (predefined)

`.sreg .v4 .u32 %ntid; // CTA shape vector` `.sreg .u32 %ntid.x, %ntid.y, %ntid.z; // CTA dimensions`

### Description

A predefined, read-only special register initialized with the number of thread ids in each CTA dimension. The %ntid special register contains a 3D CTA shape vector that holds the CTA dimensions. CTA dimensions are non-zero; the fourth element is unused and always returns zero. The total number of threads in a CTA is `(%ntid.x * %ntid.y * %ntid.z)`.

`%ntid.y == %ntid.z == 1 in 1D CTAs.` `%ntid.z ==1 in 2D CTAs.` Maximum values of `%ntid.{x,y,z}` are as follows:

.target architecture

%ntid.x

%ntid.y

%ntid.z

sm\_1x

512

512

64

sm_20, sm_3x, sm_5x, sm_6x

1024

1024

64

### PTX ISA Notes

Introduced in PTX ISA version 1.0 with type .v4.u16.

Redefined as type `.v4.u32` in PTX ISA version 2.0. For compatibility with legacy PTX code, 16-bit mov and cvt instructions may be used to read the lower 16-bits of each component of `%ntid.`

### Target ISA Notes

Supported on all target architectures.

### Examples

```c++

// compute unified thread id for 2D CTA
mov.u32  %r0,%tid.x;
mov.u32  %h1,%tid.y;
mov.u32  %h2,%ntid.x;
mad.u32  %r0,%h1,%h2,%r0;
mov.u16  %rh,%ntid.x;      // legacy code
```

## 9.3. Special Registers: `%laneid`

`%laneid` Lane Identifier.

### Syntax (predefined)

`.sreg .u32 %laneid;`

### Description

A predefined, read-only special register that returns the thread's lane within the warp. The lane identifier ranges from `zero to WARP_SZ-1.`

### PTX ISA Notes

Introduced in PTX ISA version 1.3.

### Target ISA Notes

Supported on all target architectures.

### Examples

```c++

mov.u32  %r, %laneid;
```

## 9.4. Special Registers: %warpid

`%warpid` Warp identifier.

### Syntax (predefined)

`.sreg .u32 %warpid;` Description A predefined, read-only special register that returns `the thread's warp identifier`. The warp identifier provides a unique warp number within a CTA but not across CTAs within a grid. `The warp identifier will be the same for all threads within a single warp.`

Note that `%warpid is volatile` and returns the location of a thread at the moment when read, but its value may change during execution, e.g., `due to rescheduling of threads following preemption.`For this reason, %ctaid and %tid should be used to compute a virtual warp index if such a value is needed in kernel code; `%warpid is intended mainly to enable profiling and diagnostic code to sample and log information such as work place mapping and load distribution.`

### PTX ISA Notes

Introduced in PTX ISA version 1.3.

### Target ISA Notes

Supported on all target architectures.

### Examples

```c++

mov.u32  %r, %warpid;
```

## 9.5. Special Registers: `%nwarpid`

`%nwarpid` Number of warp identifiers.

### Syntax (predefined)

`.sreg .u32 %nwarpid;`

### Description

A predefined, read-only special register that returns the `maximum number of warp identifiers.`

### PTX ISA Notes

Introduced in PTX ISA version 2.0.

### Target ISA Notes

%nwarpid requires sm\_20 or higher.

### Examples

`mov.u32 %r, %nwarpid;`

## 9.6. Special Registers: `%ctaid`

`%ctaid` CTA identifier within a grid.

### Syntax (predefined)

`.sreg .v4 .u32 %ctaid; // CTA id vector` `.sreg .u32 %ctaid.x, %ctaid.y, %ctaid.z; // CTA id components`

### Description

A predefined, read-only special register initialized with the CTA identifier within the CTA grid. The %ctaid special register contains a 1D, 2D, or 3D vector, depending on the shape and rank of the CTA grid. The fourth element is unused and always returns zero.

It is guaranteed that:

`0 <= %ctaid.x < %nctaid.x` `0 <= %ctaid.y < %nctaid.y` `0 <= %ctaid.z < %nctaid.z`

### PTX ISA Notes

Introduced in PTX ISA version 1.0 with type .v4.u16.

Redefined as type .v4.u32 in PTX ISA version 2.0. For compatibility with legacy PTX code, 16-bit mov and cvt instructions may be used to read the lower 16-bits of each component of %ctaid.

### Target ISA Notes

Supported on all target architectures.

### Examples

```c++

mov.u32  %r0,%ctaid.x;
mov.u16  %rh,%ctaid.y;   // legacy code
```

## 9.7. Special Registers: %nctaid

`%nctaid` Number of CTA ids per grid.

### Syntax (predefined)

`.sreg .v4 .u32 %nctaid // Grid shape vector` `.sreg .u32 %nctaid.x,%nctaid.y,%nctaid.z; // Grid dimensions`

### Description

A predefined, read-only special register initialized with the number of CTAs in each grid dimension. The `%nctaid` special register contains a 3D grid shape vector, with each element having a value of at least 1. The fourth element is unused and always returns zero.

Maximum values of %nctaid.{x,y,z} are as follows:

.target architecture

%nctaid.x

%nctaid.y

%nctaid.z

sm_1x, sm_20

65535

65535

65535

sm_3x, sm_5x, sm\_6x

2^31 -1

65535

65535

### PTX ISA Notes

Introduced in PTX ISA version 1.0 with type .v4.u16.

Redefined as type .v4.u32 in PTX ISA version 2.0. For compatibility with legacy PTX code, 16-bit mov and cvt instructions may be used to read the lower 16-bits of each component of %nctaid.

### Target ISA Notes

Supported on all target architectures.

### Examples

```c++

mov.u32  %r0,%nctaid.x;
mov.u16  %rh,%nctaid.x;     // legacy code
```

## 9.8. Special Registers: %smid

`%smid` SM identifier.

### Syntax (predefined)

`.sreg .u32 %smid;`

### Description

A predefined, read-only special register that returns the processor (SM) identifier on which a particular thread is executing. The SM identifier ranges `from 0 to %nsmid-1`. The SM identifier numbering is not guaranteed to be `contiguous`.

### Notes

Note that %smid is volatile and returns the location of a thread at the moment when read, but its value may change during execution, e.g. due to rescheduling of threads following preemption. %smid is intended mainly to enable profiling and diagnostic code to sample and log information such as work place mapping and load distribution.

### PTX ISA Notes

Introduced in PTX ISA version 1.3.

### Target ISA Notes

Supported on all target architectures.

### Examples

```c++

mov.u32  %r, %smid;
```

## 9.9. Special Registers: %nsmid

`%nsmid` Number of SM identifiers.

### Syntax (predefined)

`.sreg .u32 %nsmid;`

### Description

A predefined, read-only special register that returns the maximum number of SM identifiers. The SM identifier numbering is not guaranteed to be contiguous, so %nsmid may be larger than the physical number of SMs in the device.

### PTX ISA Notes

Introduced in PTX ISA version 2.0.

### Target ISA Notes

%nsmid requires sm\_20 or higher.

### Examples

```c++

mov.u32  %r, %nsmid;
```

## 9.10. Special Registers: `%gridid`

`%gridid` Grid identifier.

### Syntax (predefined)

`.sreg .u64 %gridid;`

### Description

A predefined, read-only special register initialized with the per-grid temporal grid identifier. The %gridid is used by debuggers to distinguish CTAs within concurrent (small) CTA grids.

During execution, repeated launches of programs may occur, where each launch starts a grid-of-CTAs. This variable provides the temporal grid launch number for this context.

For sm_1x targets, `%gridid` is limited to the range \[0..216-1\]. For sm_20, `%gridid` is limited to the range \[0..232-1\]. sm\_30 supports the entire 64-bit range.

### PTX ISA Notes

Introduced in PTX ISA version 1.0 as type .u16.

Redefined as type .u32 in PTX ISA version 1.3.

Redefined as type .u64 in PTX ISA version 3.0.

For compatibility with legacy PTX code, 16-bit and 32-bit mov and cvt instructions may be used to read the lower 16-bits or 32-bits of each component of %gridid.

### Target ISA Notes

Supported on all target architectures.

### Examples

```c++

mov.u64  %s, %gridid;  // 64-bit read of %gridid
mov.u32  %r, %gridid;  // legacy code with 32-bit %gridid
```

## 9.11. Special Registers: %lanemask\_eq

`%lanemask_eq` 32-bit mask with bit set in position equal to the thread's lane number in the warp.

### Syntax (predefined)

`.sreg .u32 %lanemask_eq;`

### Description

A predefined, read-only special register initialized with a 32-bit mask with a bit set in the position equal to the thread's lane number in the warp.

### PTX ISA Notes

Introduced in PTX ISA version 2.0.

### Target ISA Notes

%lanemask\_eq requires sm\_20 or higher.

### Examples

```c++

mov.u32     %r, %lanemask_eq;
```

## 9.12. Special Registers: %lanemask\_le

`%lanemask_le` 32-bit mask with bits set in positions less than or equal to the thread's lane number in the warp.

### Syntax (predefined)

`.sreg .u32 %lanemask_le;`

### Description

A predefined, read-only special register initialized with a 32-bit mask with bits set in positions less than or equal to the thread's lane number in the warp.

### PTX ISA Notes

Introduced in PTX ISA version 2.0.

### Target ISA Notes

`%lanemask_le` requires sm\_20 or higher.

### Examples

```c++

mov.u32     %r, %lanemask_le
```

## 9.13. Special Registers: %lanemask\_lt

`%lanemask_lt` 32-bit mask with bits set in positions less than the thread's lane number in the warp.

### Syntax (predefined)

`.sreg .u32 %lanemask_lt;`

### Description

A predefined, read-only special register initialized with a 32-bit mask with bits set in positions less than the thread's lane number in the warp.

### PTX ISA Notes

Introduced in PTX ISA version 2.0.

### Target ISA Notes

%lanemask\_lt requires sm\_20 or higher.

### Examples

```c++

mov.u32     %r, %lanemask_lt;
```

## 9.14. Special Registers: %lanemask\_ge

`%lanemask_ge` 32-bit mask with bits set in positions greater than or equal to the thread's lane number in the warp.

### Syntax (predefined)

`.sreg .u32 %lanemask_ge;`

### Description

A predefined, read-only special register initialized with a 32-bit mask with bits set in positions greater than or equal to the thread's lane number in the warp.

### PTX ISA Notes

Introduced in PTX ISA version 2.0.

### Target ISA Notes

%lanemask\_ge requires sm\_20 or higher.

### Examples

```c++

mov.u32     %r, %lanemask_ge;
```

## 9.15. Special Registers: %lanemask\_gt

`%lanemask_gt` 32-bit mask with bits set in positions greater than the thread's lane number in the warp.

### Syntax (predefined)

`.sreg .u32 %lanemask_gt;`

### Description

A predefined, read-only special register initialized with a 32-bit mask with bits set in positions greater than the thread's lane number in the warp.

### PTX ISA Notes

Introduced in PTX ISA version 2.0.

### Target ISA Notes

%lanemask\_gt requires sm\_20 or higher.

### Examples

```c++

mov.u32     %r, %lanemask_gt;
```

## 9.16. Special Registers: %clock, %clock\_hi

`%clock, %clock_hi` `%clock` A predefined, read-only 32-bit unsigned cycle counter. %clock\_hi The upper 32-bits of %clock64 special register.

### Syntax (predefined)

`.sreg .u32 %clock;` `.sreg .u32 %clock_hi;`

### Description

Special register %clock and %clock\_hi are unsigned 32-bit read-only cycle counters that wrap silently.

### PTX ISA Notes

`%clock` introduced in PTX ISA version 1.0.

`%clock_hi` introduced in PTX ISA version 5.0.

### Target ISA Notes

%clock supported on all target architectures.

%clock\_hi requires sm\_20 or higher.

### Examples

```c++

mov.u32 r1,%clock;
mov.u32 r2, %clock_hi;
```

## 9.17. Special Registers: %clock64

`%clock64` A predefined, read-only 64-bit unsigned cycle counter.

### Syntax (predefined)

`.sreg .u64 %clock64;`  

### Description

Special register %clock64 is an unsigned 64-bit read-only cycle counter that wraps silently.

### Notes

The lower 32-bits of %clock64 are identical to %clock.

The upper 32-bits of %clock64 are identical to %clock\_hi.

### PTX ISA Notes

Introduced in PTX ISA version 2.0.

### Target ISA Notes

%clock64 requires sm\_20 or higher.

### Examples

```c++

mov.u64  r1,%clock64;
```

## 9.18. Special Registers: %pm0..%pm7

`%pm0..%pm7` Performance monitoring counters.

### Syntax (predefined)

`.sreg .u32 %pm<8>;`  

### Description

Special registers %pm0..%pm7 are unsigned 32-bit read-only performance monitor counters. Their behavior is currently undefined.

### PTX ISA Notes

%pm0..%pm3 introduced in PTX ISA version 1.3.

%pm4..%pm7 introduced in PTX ISA version 3.0.

### Target ISA Notes

%pm0..%pm3 supported on all target architectures.

%pm4..%pm7 require sm\_20 or higher.

### Examples

```c++

mov.u32  r1,%pm0;
mov.u32  r1,%pm7;
```

## 9.19. Special Registers: %pm0_64..%pm7_64

`%pm0_64..%pm7_64` 64 bit Performance monitoring counters.

### Syntax (predefined)

`.sreg .u64 %pm0_64;` `.sreg .u64 %pm1_64;` `.sreg .u64 %pm2_64;` `.sreg .u64 %pm3_64;` `.sreg .u64 %pm4_64;` `.sreg .u64 %pm5_64;` `.sreg .u64 %pm6_64;` `.sreg .u64 %pm7_64;`

### Description

Special registers %pm0_64..%pm7_64 are unsigned 64-bit read-only performance monitor counters. Their behavior is currently undefined.

### Notes

The lower 32bits of %pm0_64..%pm7_64 are identical to %pm0..%pm7.

### PTX ISA Notes

%pm0_64..%pm7_64 introduced in PTX ISA version 4.0.

### Target ISA Notes

%pm0_64..%pm7_64 require sm\_50 or higher.

### Examples

```c++

mov.u32  r1,%pm0_64;
mov.u32  r1,%pm7_64;
```

## 9.20. Driver-defined read-only registers:`%envreg<32>`.

### Syntax (predefined)

`.sreg .b32 %envreg<32>;`  

### Description

A set of 32 pre-defined read-only registers used to capture execution environment of PTX program outside of PTX virtual machine. These registers are initialized by the driver prior to kernel launch and can contain cta-wide or grid-wide values.

Precise semantics of these registers is defined in the driver documentation.

### PTX ISA Notes

Introduced in PTX ISA version 2.1.

### Target ISA Notes

Supported on all target architectures.

### Examples

$$mov.b32 %r1,%envreg0; // move envreg0 to %r1$$

## 9.21. Special Registers: %globaltimer, %globaltimer\_lo, %globaltimer\_hi

%globaltimer, %globaltimer\_lo, %globaltimer\_hi %globaltimer A predefined, 64-bit global nanosecond timer. %globaltimer\_lo The lower 32-bits of %globaltimer. %globaltimer\_hi The upper 32-bits of %globaltimer.

### Syntax (predefined)

`.sreg .u64 %globaltimer;` `.sreg .u32 %globaltimer_lo, %globaltimer_hi;`

### Description

Special registers intended for use by NVIDIA tools. The behavior is target-specific and may change or be removed in future GPUs. When JIT-compiled to other targets, the value of these registers is unspecified.

### PTX ISA Notes

Introduced in PTX ISA version 3.1.

### Target ISA Notes

Requires target sm\_30 or higher.

### Examples

```c++

mov.u64  r1,%globaltimer;
```

## 9.22. Special Registers: `%total_smem_size`

`%total_smem_size` Total size of shared memory used by a CTA of a kernel.

### Syntax (predefined)

`.sreg .u32 %total_smem_size;`

### Description

A predefined, read-only special register initialized with total size of shared memory allocated (statically and dynamically) for the CTA of a kernel at launch time.

Size is returned in multiples of shared memory allocation unit size supported by target architecture.

Allocation unit values are as follows:

Target architecture

Shared memory allocation unit size

sm\_2x

128 bytes

sm_3x, sm_5x, sm\_6x

256 bytes

### PTX ISA Notes

Introduced in PTX ISA version 4.1.

### Target ISA Notes

Requires sm\_20 or higher.

### Examples

```c++

mov.u32  %r, %total_smem_size;
```

## 9.23. Special Registers: %dynamic\_smem\_size

`%dynamic_smem_size` Size of shared memory allocated dynamically at kernel launch.

### Syntax (predefined)

`.sreg .u32 %dynamic_smem_size;`

### Description

Size of shared memory allocated dynamically at kernel launch.

A predefined, read-only special register initialized with size of shared memory allocated dynamically for the CTA of a kernel at launch time.

### PTX ISA Notes

Introduced in PTX ISA version 4.1.

### Target ISA Notes

Requires sm\_20 or higher.

### Examples

```c++

mov.u32  %r, %dynamic_smem_size;
```