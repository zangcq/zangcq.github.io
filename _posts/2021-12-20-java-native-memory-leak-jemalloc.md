---
title: 使用 jemalloc 定位 Java Native Memory 泄漏
date: 2021-12-20
categories:
  - jvm
tags:
  - java
  - jemalloc
  - memory-leak
  - native-memory
  - troubleshooting
excerpt: 进程 RSS 持续上涨，堆内存却正常？借助 jemalloc profiling 将凶手锁定在未关闭的 GZIPOutputStream。
---

Java 进程内存一直涨，但堆内看起来挺正常，GC 也没异常——这种场景你大概率遇到过。堆没问题不代表万事大吉，JNI、压缩库、DirectByteBuffer、线程栈、甚至内存分配器的碎片，都能把 RSS 推上去，最后触发容器 OOM 或者直接被操作系统 kill。

这篇文章记录一次完整的排查过程：用 jemalloc 的 profiling 能力抓 native 分配的热点，发现 zlib 压缩链路占了将近 70%，再结合 Java 线程栈和代码 review，确认是异常处理里没关 `GZIPOutputStream`。

> 说明：业务名称、内部平台链接、仓库路径、人员信息和监控截图已移除；命令中的路径也替换成了通用示例。

## 1. 问题现象

应用跑着跑着进程内存就一直涨。看 Java 堆和 GC 都没发现能和 RSS 增幅对上的异常，但进程最后还是因为超内存限制退出了。

碰到这种情况，先得搞清楚几个概念：

- **Java Heap**：GC 管的，`-Xms` / `-Xmx` 控制。
- **Direct Memory**：主要来自 `DirectByteBuffer`，一般受 `-XX:MaxDirectMemorySize` 约束。
- **Native Memory**：范围大得多——JNI 分配、线程栈、Metaspace、Code Cache、GC 内部结构、分配器碎片都算。
- **RSS**：操作系统看到的进程实际占用的物理内存，不等于堆，也不等于 Direct Memory。

所以，"堆没涨但 RSS 一直涨"，只能说大概率是堆外的问题，不能一口咬定是 Direct Memory 泄漏。

## 2. 排查思路

面对疑似 Native Memory 泄漏，我习惯按这个顺序缩小范围：

1. 对比 Heap、Direct Buffer、NMT、进程 RSS 的变化趋势。
2. 确认是不是线程数、类加载、JIT Code Cache 或 GC 结构变化引起的。
3. 如果还不确定，上 jemalloc / tcmalloc / eBPF 采样 `malloc` 调用栈。
4. 把 native 分配热点和 Java 线程栈、业务调用链、源码生命周期串起来分析。
5. 修完以后用同等负载、同等时长对照验证。

这个 case 里，常规 JVM 指标解释不了 RSS 的持续增长，所以进一步用了 jemalloc profiling。

## 3. 构建支持 Profiling 的 jemalloc

jemalloc 默认不开启 profiling，得自己编译：

```bash
git clone https://github.com/jemalloc/jemalloc.git
cd jemalloc
./autogen.sh --enable-prof
make -j"$(nproc)"
make install
```

搞之前确认几件事：

- jemalloc 和你的 OS、CPU 架构、glibc 版本兼容；
- 应用允许通过 `LD_PRELOAD` 换分配器；
- profiling 有额外开销（CPU、内存、磁盘），dump 目录空间够用；
- 最好先在灰度或可复现环境验证一把。

## 4. 启动应用并采集 Heap Profile

通过 `LD_PRELOAD` 让 Java 进程用上 jemalloc，`MALLOC_CONF` 开启采样：

```bash
export LD_PRELOAD="/usr/local/lib/libjemalloc.so"
export MALLOC_CONF="prof:true,lg_prof_interval:25,lg_prof_sample:18,prof_prefix:/tmp/jeprof"

exec "$JAVA_HOME/bin/java" \
  -jar application.jar
```

参数含义：

- `prof:true`：开 profiling。
- `lg_prof_interval:25`：累计分配每达到约 2^25 字节 dump 一次。
- `lg_prof_sample:18`：平均每 2^18 字节采样一次。
- `prof_prefix:/tmp/jeprof`：dump 文件前缀。

interval 是按**累计分配字节数**触发的，不是按时间。参数越激进越详细，但开销也越大。

启动后目标目录会持续生成：

```text
/tmp/jeprof.<pid>.<seq>.heap
```

想看一段时间内的净增长，要找不同时间点的 profile 对比，别只看单个快照的累计分配热点。

## 5. 生成内存分配调用图

装好 Graphviz 后，用 jemalloc 自带的 `jeprof` 生成图：

```bash
# Debian/Ubuntu
apt-get install graphviz

jeprof \
  --show_bytes \
  "$JAVA_HOME/bin/java" \
  /tmp/jeprof.<pid>.<seq>.heap \
  --gif > jeprof.heap.gif
```

看图的时候重点留意：

- 占用字节数持续往上走的路径；
- 多个时间点都在且降不下来的热点；
- zlib、OpenSSL、Netty、JNI 扩展等 native library 的分配函数；
- 没解析出来的符号附近的上下游函数；
- "累计分配高" 和 "当前存活高" 不是一回事。

这个 case 里，zlib `inflate` / 压缩相关链路占了约 69%。但光靠这张图还不能确定是哪段 Java 代码导致的。

## 6. 从 Native 热点回到 Java 调用栈

调用图里可能出现未解析的 native symbol，原因很多：缺调试符号、被 strip、JIT 代码映射不上、动态库路径不一致、Java 到 native 的边界没展开等等。

这时候可以两个方向补证据：

### 6.1 用 async-profiler

async-profiler 能同时看 Java、native 和内核栈。环境允许的话，采 allocation、CPU 或 native 事件，看看压缩库热点上面是哪些 Java 方法。

### 6.2 用 jcmd 抓线程栈

```bash
jcmd <pid> Thread.print -l > thread-dump.txt
```

搜 `GZIPOutputStream`、`Inflater`、`Deflater`、压缩入口、异常日志处理代码，确认哪些 Java 路径会进入对应的 native 方法。

这个 case 里，压缩链路的线程栈最终指向了一段异常信息压缩逻辑。

## 7. 根因：压缩流没关

问题代码在异常日志处理里创建了 `GZIPOutputStream`，但有的路径没关流。简化后的错误示范：

```java
byte[] compress(byte[] input) throws IOException {
    ByteArrayOutputStream output = new ByteArrayOutputStream();
    GZIPOutputStream gzip = new GZIPOutputStream(output);
    gzip.write(input);
    gzip.finish();
    return output.toByteArray();
}
```

`finish()` 只负责把压缩数据写完，不等于 `close()`。`GZIPOutputStream` 底层用 `Deflater`，`close()` 才会释放关联的 native zlib 资源。如果对象生命周期被拉长、或者清理没及时跑，native 内存就会一直堆着。

正确姿势是 try-with-resources：

```java
byte[] compress(byte[] input) throws IOException {
    ByteArrayOutputStream output = new ByteArrayOutputStream();

    try (GZIPOutputStream gzip = new GZIPOutputStream(output)) {
        gzip.write(input);
    }

    return output.toByteArray();
}
```

try-with-resources 保证正常返回和抛异常都能走到 `close()`。持有 native 资源的 Java 对象，别指望 GC、finalizer 或 Cleaner 来兜底，那不可靠。

实在受限于旧代码结构，至少也得在 `finally` 里关：

```java
GZIPOutputStream gzip = null;
try {
    gzip = new GZIPOutputStream(output);
    gzip.write(input);
} finally {
    if (gzip != null) {
        gzip.close();
    }
}
```

新代码直接上 try-with-resources，对异常传播和 suppressed exception 的处理也更完善。

## 8. 修复验证

修完别急着上线，用和问题现场尽量一样的条件验证：

- 同样流量、并发、数据规模；
- 跑够原来稳定复现所需的时间；
- 同时观察 Heap、RSS、Direct Buffer、GC 和容器内存；
- 再次采 jemalloc profile，对比热点路径的存活内存；
- 异常路径和高频日志路径都要覆盖，别只测正常流程。

修完应该看到：RSS 不再单调涨、Heap / GC 稳定、zlib 相关的 native 分配不再累积、长时间压测不触发 OOM。

## 9. 容易踩的坑

**把所有堆外问题都归给 Direct Memory。** DirectByteBuffer 只是 Native Memory 的一部分。native library、线程栈、类元数据、JIT、GC 结构、分配器碎片都可能导致 RSS 涨。

**把高累计分配量当泄漏。** 热点函数分配频繁不等于没释放。判断泄漏要看不同时间点的存活量或净增长，结合稳定负载下的趋势。

**觉得有 GC 就不用显式释放资源。** GC 管 Java 对象可达性，不管文件描述符、Socket、压缩上下文等 native 资源。实现了 `AutoCloseable` 的对象，都应该在明确的作用域里关闭。

**只验证正常路径。** 这个 case 的问题出在异常处理逻辑。资源泄漏经常藏在异常、超时、重试和提前返回这些分支里，必须专门覆盖。

## 10. 总结

一条清晰的证据链：

1. **监控定界**：Heap 解释不了 RSS 增长，方向转向 Native Memory。
2. **分配采样**：jemalloc 调用图显示 zlib 压缩链路异常。
3. **栈与代码关联**：线程栈把 native 热点映射到异常日志压缩逻辑。
4. **生命周期审查**：`GZIPOutputStream` 部分路径未关闭。
5. **修复验证**：显式关闭后内存恢复正常，OOM 消失。

排查 Native Memory 的核心不是一次猜中根因，而是持续缩小范围：先区分 Heap 和 RSS，再用分配器 profiling 找 native 热点，最后回到 Java 调用链检查资源生命周期。

**善用工具，大胆假设，用完整证据链小心验证。**

> 相关阅读：[从 Netty 堆外内存到 glibc Arena：一次 RSS 异常增长排查](/posts/java-offheap-memory-rss-gap/)——另一个堆外内存排查案例，根因在 glibc 的 Arena 缓存策略。

## 参考资料

- [jemalloc 官方仓库](https://github.com/jemalloc/jemalloc)
- [Debugging Java Native Memory Leaks](https://www.evanjones.ca/java-native-leak-bug.html)
- [Java try-with-resources 官方教程](https://docs.oracle.com/javase/tutorial/essential/exceptions/tryResourceClose.html)