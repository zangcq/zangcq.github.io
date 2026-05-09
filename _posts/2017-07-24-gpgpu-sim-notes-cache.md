---
title: "GPGPU-Sim Notes —— Cache"
date: 2017-07-24 15:22:14
categories: ["GPGPU-Sim Notes"]
tags: ["Cache", "GPU"]
permalink: "/2017/07/24/gpgpu-sim-notes-cache/"
legacy: true
toc: true
classes: wide
---

# GPGPU-Sim笔记整理 cache

## gpgpu-cache.cc

本文件主要分为三部分：

一；tag array

二；MSHR

三；CACHE

**.h文件**

主要定义了

#### 枚举类型

名称| 定义| 内容
---|---|---
cache_block_state| 定义cache行的状态|  INVALID（无效的）,RESERVED（保留） VALID（有效）,MODIFIED（修改的，dirty）
cache_request_status| cache请求的状态| HIT/MISSHIT_RESERVED(命中保留，表示数据在L2 -INCT队列中)RESERVATION_FAIL
cache_event| 访问cache的事件| WRITE_BACK_REQUEST_SENT,写回请求READ_REQUEST_SENT, 读请求WRITE_REQUEST_SENT 写请求
replacement_policy_t| cache 替换策略|  LRU, FIFO,
write_policy_t| cache 写策略|  READ_ONLY, 只读 WRITE_BACK, 写回 WRITE_THROUGH,写直达 WRITE_EVICT, 写剔除 LOCAL_WB_GLOBAL_WT 局部写回 全局写直达
allocation_policy_t| 分配策略在miss时，是否将数据填入cache。|  ON_MISS, 不将数据填入cache ON_FILL 将数据填入cache
mshr_config_t| MSHR 的配置方法| TEX_FIFO,用于texture（纹理cache）ASSOC//用于普通cache
set_index_function| 用于set 索引号的方法|  FERMI_HASH_SET_FUNCTION = 0,费米哈希设置 LINEAR_SET_FUNCTION, 线性设置 CUSTOM_SET_FUNCTION ？？？？？

#### 结构体

cache_block_t| cache块结构|  new_addr_type m_tag; new_addr_type m_block_addr; unsigned m_alloc_time; unsigned m_last_access_time; unsigned m_label; unsigned m_eacnt; unsigned m_lru; unsigned m_fill_time; cache_block_state m_status;
---|---|---
cache_sub_stats| cache统计信息| accessmisspending hitreservation
extra_mf_fields| 在data_cache 类的在texture_cachel类中也有不知道啥意思|  bool m_valid; new_addr_type m_block_addr; unsigned m_cache_index; unsigned m_data_size;
fragment_entry| texture_cache| mem_fetch *m_request; // request informationunsigned m_cache_index; where to look for databool m_miss; // true if sent memory requestunsigned m_data_size;
rob_entry| texture_cache| bool m_ready;unsigned m_time; // which cycle did this entry become ready?unsigned m_index; // where in cache should block be placed?mem_fetch *m_request;new_addr_type m_block_addr;
data_block| texture_cache| bool m_valid; new_addr_type m_block_addr;
extra_mf_fields| texture_cache|  bool m_valid; unsigned m_rob_index;

####  tag_array()

类名| 描述| 重点说明
---|---|---
cache_config| cache配置的类| 主要作用是初始化cache；读取配置文件gpgpu.config中的参数重要函数init()：读入配置参数，初始化cacheset_index():设置cache块索引tag（）：读取tag位
l1d_cache_configl2_cache_config| 继承cache_config|
tag_array| 详见cache基础| 重要函数;probe():查找cache中的块实现LRU策略access():实现cache 策略的主要功能函数fill（） 实现对cache的填充flush（）冲刷，清空
mshr_table| MSHR表，用来存放miss轨迹的| 重要函数：probefulladd
cache_stats| cache统计信息的类| 主要统计cache的访问次数，命中率利用率等等
cache_t| 所有cache的父类| 继承关系详见cache继承关系
baseline_cache| |

1.理解一下cache结构tag

For generality, the tag includes both index and tag. This allows for more complex set index calculations that can result in different indexes mapping to the same set, thus the full tag + index is required to check for hit/miss. Tag is now identical to the block address.

tag（标记字段）通常包括index（索引）和tag（标记）。这样允许我们设置更复杂的索引计算，会导致不同的索引映射到同一个set（cache存储单元）里，因此满的 tag+index 需要进行检查是否命中。现在tag和block地址是相同的。

#### cache 继承关系

*(Legacy image unavailable; original hosted on old site.)*
