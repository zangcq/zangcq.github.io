---
title: PTX ISA 之 Control Flow Instructions
tags:
  - GPU
  - PTX ISA
id: '139'
categories:
  - - gpu-computing
    - GPU PTX ISA Analysis
date: 2017-06-29 10:26:19
---

# Control Flow Instructions

The following PTX instructions and syntax are for controlling execution in a PTX program:

`{}` `@` `bra` `call` `ret` `exit`

## 1.1. Control Flow Instructions: {}

`{}` Instruction grouping.

作为指令组存在，相当于指令列表，在ptx中作为kernel函数的分界。

### Syntax

`{ instructionList }`

### Description

The curly braces create a group of instructions, used primarily for defining a function body. The curly braces also provide a mechanism for determining the scope of a variable: any variable declared within a scope is not available outside the scope.

同时作为变量的作用域。

### PTX ISA Notes

Introduced in PTX ISA version 1.0.

### Target ISA Notes

Supported on all target architectures.

在sass 中也会出现`{}`，其作用是？

### Examples

$${ add.s32 a,b,c; mov.s32 d,a; }$$

## 1.2. Control Flow Instructions: @

`@` Predicated execution.

作为谓词执行的标志。

### Syntax

`@{!}p instruction;`

### Description

Execute an instruction or instruction block for threads that have the guard predicate True. Threads with a False guard predicate do nothing.

作为条件判断的指令标志，如果`p`为真，则执行指令，否则 不执行指令。

### Semantics

`If {!}p` then instruction

### PTX ISA Notes

Introduced in PTX ISA version 1.0.

### Target ISA Notes

Supported on all target architectures.

### Examples

```c

setp.eq.f32  p,y,0;         // is y zero?
@!p div.f32      ratio,x,y  // avoid division by zero
@q  bra L23;                // conditional branch
```

## 1.3. Control Flow Instructions: bra

`bra` Branch to a target and continue execution there.

作为分支指令，用作跳转。

### Syntax

```c

@p   bra{.uni}  tgt;             // direct branch, tgt is a label 
bra{.uni}  tgt;                  // unconditional branch
@p   bra{.uni}  tgt{, tlist};    // indirect branch, tgt is reg
bra{.uni}  tgt{, tlist};
```

tgt = target 作为要跳转的目标 label， 分为有条件和无条件跳转。

### Description

Continue execution at the target. Conditional branches are specified by using a guard predicate. The branch target must be a label. The branch target can be either a label or an address of a label held in a register.

继续在target上执行，目标必须是 label 或者存储 label的地址，TARGET 通常是 一个 basic block 形如`BB1_3`

`bra.uni`is guaranteed to be non-divergent, meaning that all threads in a warp have identical values for the guard predicate and branch target.

`uni`表示无 warp 分歧，同一个warp中的线程，都走同一个分支。

Indirect branches support an optional second operand, `tlist`, to communicate the list of potential targets. This operand is either the name of an array (jump table) initialized to a list of labels; or a label associated with a `.branchtargets` directive, which declares a list of potential target labels. The`tgt`register must hold the address of one of the control flow labels in the jump table or `.branchtargets`list indicated by`tlist`.

非直接分支，可能是一个label的列表，通过寄存器存储了label的地址。

If no tlist is provided, the branch target may be any label within the current function whose address is taken (i.e., any label used in a variable initialize or as the source operand of a mov instruction. Note that if no `tlist`is given, the optimizer will build a conservative control flow graph which may degrade performance. If `tlist` is given and the actual target is not in `tlist`, the code is incorrect and the program may generate incorrect results or fail to execute.

如果 label列表不给出，那么编译器就会生成一个保守并且性能降低的cfg，如果给定了label 列表，但是真正的label 不在其中，那便会导致错误的结果或者不能执行。

Jump tables and `.branchtargets` declarations must be within the local function scope and refer only to control flow labels within the current function. Jump tables may be defined in either the constant or global state space.

跳转 label 和 branch 声明，必须在当前的kernel里，不能跳到别的kernel 中。个人理解

### Semantics

```c

if (p) {
pc = tgt;
}
```

### PTX ISA Notes

Direct branch introduced in PTX ISA version 1.0.

Indirect branch introduced in PTX ISA version 2.1.

Note: indirect branch is currently unimplemented.

### Target ISA Notes

Direct branch supported on all target architectures.

Indirect branch requires sm\_20 or higher.

### Examples

```c

bra.uni  L_exit;        // uniform unconditional jump
@q  bra      L23;       // conditional branch

// indirect branch using jump table
.global .u32 jmptbl[5] = { Loop, Done, L1, L2, L3 };
...
@p  ld.global.u32  %r0, [jmptbl+4];//L2
@q  ld.global.u32  %r0, [jmptbl+8];//？
bra            %r0, jmptbl;

// indirect branch using .branchtargets directive
...
@p  mov.u32  %r0, Done;
@q  mov.u32  %r0, L1;
Btgt: .branchtargets Done, L1;
bra      %r0, Btgt;
//  如果执行了，，那就跳到L1
//  indirect branch with no target list provided
...
@p  mov.u32  %r0, Done;
@q  mov.u32  %r0, L1;
bra      %r0;
```

### 1.4. Control Flow Instructions: call

**call** Call a function, recording the return location.

调用一个函数，并记录返回位置。

### Syntax

```c

// direct call to named function, func is a symbol
call{.uni} (ret-param), func, (param-list);
call{.uni} func, (param-list);
call{.uni} func;

// indirect call via pointer, with full list of call targets
call{.uni} (ret-param), fptr, (param-list), flist;
call{.uni} fptr, (param-list), flist;
call{.uni} fptr, flist;

// indirect call via pointer, with no knowledge of call targets
call{.uni} (ret-param), fptr, (param-list), fproto;
call{.uni} fptr, (param-list), fproto;
call{.uni} fptr, fproto;
```

### Description

The call instruction stores the address of the next instruction, so execution can resume at that point after executing a `ret` instruction.

call指令可以保存下一条指令，因此可以在`ret`之后回到原来的执行点。

A call is assumed to be divergent unless the .`uni` suffix is present, indicating that the call is guaranteed to be non-divergent, meaning that all threads in a warp have identical values for the guard predicate and call target.

For direct calls, the called location `func` must be a symbolic function name; for indirect calls, the called location `fptr` must be an address of a function held in a register. Input arguments and return values are optional. Arguments may be registers, immediate constants, or variables in `.param` space. Arguments are pass-by-value.

_直接_ 调用的时候，可以直接调用函数名，也可以调用函数的地址。参数同 值来 传递。

Indirect calls require an additional operand, `flist`or `fproto`, to communicate the list of potential call targets or the common function prototype of all call targets, respectively. In the first case, `flist` gives a complete list of potential call targets and the optimizing `backend`is free to optimize the calling convention. In the second case, where the complete list of potential call targets may not be known, the common function prototype is given and the call must obey the ABI's calling convention.

非直接调用，需要一个额外的参数。

The `flist` operand is either the name of an array (call table) initialized to a list of function names; or a label associated with a `.calltargets` directive, which declares a list of potential call targets. In both cases the fptr register holds the address of a function listed in the call table or `.calltargets` list, and the call operands are type-checked against the type signature of the functions indicated by `flist`.

The `fproto` operand is the name of a label associated with a `.callprototype` directive. This operand is used when a complete list of potential targets is not known. The call operands are type-checked against the prototype, and code generation will follow the `ABI` calling convention. If a function that doesn't match the prototype is called, the behavior is undefined.

Call tables may be declared at module scope or local scope, in either the constant or global state space. The `.calltargets` and `.callprototype` directives must be declared within a function body. All functions must be declared prior to being referenced in a call table initializer or `.calltargets` directive.

### PTX ISA Notes

Direct call introduced in PTX ISA version 1.0. Indirect call introduced in PTX ISA version 2.1.

### Target ISA Notes

Direct call supported on all target architectures. Indirect call requires sm\_20 or higher.

### Examples

$$// examples of direct call call init; // call function 'init' call.uni g, (a); // call function 'g' with parameter 'a' @p call (d), h, (a, b); // return value into register d // call-via-pointer using jump table .func (.reg .u32 rv) foo (.reg .u32 a, .reg .u32 b) ... .func (.reg .u32 rv) bar (.reg .u32 a, .reg .u32 b) ... .func (.reg .u32 rv) baz (.reg .u32 a, .reg .u32 b) ... .global .u32 jmptbl\[5\] = { foo, bar, baz }; ... call (retval), %r0, (x, y), jmptbl; @p ld.global.u32 %r0, \[jmptbl+4\]; @p ld.global.u32 %r0, \[jmptbl+8\]; // call-via-pointer using .calltargets directive .func (.reg .u32 rv) foo (.reg .u32 a, .reg .u32 b) ... .func (.reg .u32 rv) bar (.reg .u32 a, .reg .u32 b) ... .func (.reg .u32 rv) baz (.reg .u32 a, .reg .u32 b) ... ... @p mov.u32 %r0, foo; @q mov.u32 %r0, baz; Ftgt: .calltargets foo, bar, baz; call (retval), %r0, (x, y), Ftgt; // call-via-pointer using .callprototype directive .func dispatch (.reg .u32 fptr, .reg .u32 idx) {... Fproto: .callprototype \_ (.param .u32 \_, .param .u32 \_); call %fptr, (x, y), Fproto; ...$$

## 1.5. Control Flow Instructions: ret

_ret_ Return from function to instruction after call.

在函数调用结束后调用后返回。

### Syntax

`ret{.uni};`

### Description

Return execution to caller's environment. A divergent return suspends threads until all threads are ready to return to the caller. This allows multiple divergent `ret`instructions.

A `ret` is assumed to be divergent unless the`.uni`suffix is present, indicating that the return is guaranteed to be non-divergent.

Any values returned from a function should be moved into the return parameter variables prior to executing the `ret` instruction.

A return instruction executed in a top-level entry routine will terminate thread execution.

### PTX ISA Notes

Introduced in PTX ISA version 1.0.

### Target ISA Notes

Supported on all target architectures.

### Examples

$$ret; @p ret;$$

## 1.6. Control Flow Instructions: exit

_exit_ Terminate a thread.

终止一个线程

### Syntax

`exit;`

### Description

Ends execution of a thread.

As threads exit, barriers waiting on all threads are checked to see if the exiting threads are the only threads that have not yet made it to a barrier for all threads in the CTA. If the exiting threads are holding up the barrier, the barrier is released.

当所有线程退出，栅栏在等待所有线程并且检查CTA中所有线程是否到达，如果退出的线程需要到达这个barrier ，那么这个barrier 就可以释放了。

### PTX ISA Notes

Introduced in PTX ISA version 1.0.

### Target ISA Notes

Supported on all target architectures.

### Examples

```c

exit;
@p  exit;
```