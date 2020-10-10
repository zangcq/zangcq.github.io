---
title: 区块链中 Gas 计算理解
tags: []
id: '1279'
categories:
  - - 程序人生
comments: false
date: 2020-05-08 11:31:32
---

# 概念理解

Gas

*   作为一个以太坊的计量单位。
*   对 算力消耗进行量化的设计指标。
*   直接翻译为天然气也可以
    *   一个合约可以理解为炒一个菜
    *   炒这道菜要N多步骤，大概消耗 1L Gas
    *   Gas Limit
        *   就是说这道菜最多用1.5L，超过了就抄不了了
    *   Gas Price
        *   这里讲的是与ETH的换算，相当于天然气多少钱一升？1块？
    *   Gas Used
        *   实际的使用量，比如上边说的 1 L
    *   Fees
        *   就是实际花了多少钱
        *   Fees  = Gas Price \* Gas Used

*   当然这里的Gas Limit 和 Gas Price 需要设置
*   为啥要用gas来做计算单位呢？

[https://ethereum.stackexchange.com/questions/3/what-is-meant-by-the-term-gas](https://ethereum.stackexchange.com/questions/3/what-is-meant-by-the-term-gas)

因为eth就像股票一样，有涨有跌，所以呢算起来比较麻烦，因此用一个无关的计量单位，然后再按市场价结算。

# Gas计算

[https://yuque.antfin-inc.com/xueyin.pxy/qxrlty/dpckl1](https://yuque.antfin-inc.com/xueyin.pxy/qxrlty/dpckl1)

Gas计算呢就是为了做这个检查，每个wasm合约都是由很多操作组成的，比如get 、add、load之类的指令；类比X86 ISA，每条指令对应的时钟周期数是不一样的，那么消耗的Gas也就不一样，因此要对整个合约消耗的gas进行一个计算，看一下是不是超过了gas limit。

*   每条 wasm 操作对应的消耗gas数

[https://github.com/djrtwo/evm-opcode-gas-costs/blob/master/opcode-gas-costs\_EIP-150\_revision-1e18248\_2017-04-12.csv](https://github.com/djrtwo/evm-opcode-gas-costs/blob/master/opcode-gas-costs_EIP-150_revision-1e18248_2017-04-12.csv)

*   那么total gas used =  SUM (wasm\_op \* wasm\_op\_gas\_cost)

## 泰瑞组的实现

在 Basic Block level进行统计，每个程序块进行一个sum，然后最后再加起来。

*   有一个疑问？
    *   加了这个计算之后，有没有对计算本身的gas消耗有影响呢？
    *   比如，加了一条计算gas的check，是不是也要gas-1之类的操作呢？

举例说明

 # gas\_leavings 当前剩余gas = gas limit - gas used
 if () {
 block 1 {
   gas\_cost = op1\*op1\_cost + op2\*op2\_cost + op3\*op3\_cost
   new\_gas\_leavings = old\_gas\_leavings - gas\_cost
   # gas\_leavings > 0 这里是一个限制条件
   op1
   op2
   op3
 ​
 }
 }
 else{}
 ​
Reference

> [https://support.blockchain.com/hc/en-us/articles/360027772571-What-is-gas-](https://support.blockchain.com/hc/en-us/articles/360027772571-What-is-gas-) [https://ethereum.stackexchange.com/questions/3/what-is-meant-by-the-term-gas](https://ethereum.stackexchange.com/questions/3/what-is-meant-by-the-term-gas)

> [https://www.zhihu.com/search?type=content&q=%E5%8C%BA%E5%9D%97%E9%93%BE%E4%B8%AD%E7%9A%84gas](https://www.zhihu.com/search?type=content&q=%E5%8C%BA%E5%9D%97%E9%93%BE%E4%B8%AD%E7%9A%84gas)

# 字节码联盟实现方案

AOT [https://github.com/bytecodealliance/wasm-micro-runtime](https://github.com/bytecodealliance/wasm-micro-runtime)

JIT [https://github.com/bytecodealliance/wasmtime](https://github.com/bytecodealliance/wasmtime)