---
title: compare in cuda ptx isa
tags:
  - CUDA
  - GPU
id: '111'
categories:
  - - programming
    - CUDA Programming
  - - gpu-computing
    - GPU PTX ISA Analysis
date: 2017-06-19 09:42:47
---

## comparitions in cuda ptx

## integer

meaning

signed op

unsigned op

bit-size op

a == b

eq

eq

eq

a != b

ne

ne

ne

a < b

lt

lo

a <= b

le

ls

a > b

gt

hi

a >= b

ge

hi

## floating

If either operand is NaN, the result is False

**meaning**

**Floating-Point Operator**

**a == b && !isNaN(a) && !isNaN(b)**

**eq**

**a != b && !isNaN(a) && !isNaN(b)**

**ne**

**a < b && !isNaN(a) && !isNaN(b)**

**lt**

**a <= b && !isNaN(a) && !isNaN(b)**

**le**

**a > b && !isNaN(a) && !isNaN(b)**

**gt**

**a >= b && !isNaN(a) && !isNaN(b)**

**ge**