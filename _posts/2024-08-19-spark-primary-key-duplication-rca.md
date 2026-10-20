---
title: Spark 主键重复问题根因分析：一次由旧版 JDK C2 优化缺陷引发的数据异常
date: 2024-08-19
categories:
  - jvm
tags:
  - jvm
  - spark
  - jdk8
  - c2
  - jit
  - unsafe
  - troubleshooting
excerpt: 小概率主键重复、地址异常、JVM 崩溃——排查后确认不是业务逻辑问题，而是旧版 JDK 8 C2 编译器对非对齐 Unsafe 写入的错误优化导致的内存清零缺陷。
---

# Spark 主键重复问题根因分析：一次由旧版 JDK C2 优化缺陷引发的数据异常

## 结论

在某些 Spark 作业中，曾观察到小概率主键重复、地址异常、甚至 JVM 崩溃等现象。排查后确认：问题并非业务逻辑或 Spark 层线程竞争导致，而是旧版 JDK 8 中一个已知 C2 编译器优化缺陷触发了错误的内存清零行为。

该缺陷对应 OpenJDK 修复项：

- [JDK-8202414](https://bugs.openjdk.org/browse/JDK-8202414)
- [OpenJDK 8u 修复提交](https://github.com/openjdk/jdk8u/commit/0ecf17c5bfb99bdff5bbcc2f2e081508a7416d63)

简要来说，当代码在对象或数组分配后立即通过 `Unsafe` 执行非对齐写入时，旧版 JDK 的 C2 优化可能错误地将“对象初始化清零”和“后续写入”合并处理，进而计算出错误的清零范围，导致数组内容被意外写入 `0x00`。在 Spark 内部大量使用 `Unsafe` 和直接内存操作的场景下，这类错误可能进一步表现为数据损坏、地址截断、读取异常或 JVM 崩溃。

推荐修复方式是升级到包含该 OpenJDK 修复的 JDK 版本；若短期无法升级，可通过规避非对齐 `Unsafe` 写入或禁用相关热点方法的 C2 编译作为临时缓解手段。

## 现象

在部分 Spark 任务中，偶发出现主键重复问题。异常具备以下特点：

1. 发生概率低，难以稳定复现；
2. 有时伴随 JVM core dump，有时不会崩溃；
3. 从不同失败现场看，表象并不完全一致；
4. 业务代码打印关键变量后，未发现明显逻辑错误或线程竞争。

典型表现包括：

- 访问对象地址异常，疑似 `baseObject` 或偏移量错误，最终导致越界访问；
- 某些地址值被截断，低位或高位字段异常；
- 在部分场景下没有立即崩溃，但后续读取到的数据已经被污染；
- Spark 内部结构在 `Unsafe` 读写后出现不可预期的字段值变化。

这类现象表面上容易被误判为 Spark 执行层的数据竞争、序列化问题或 off-heap/on-heap 地址管理错误，但进一步分析后发现，它们可以由同一个 JVM 编译器缺陷统一解释。

## 定位过程

首先，对相关 Spark 执行路径进行了代码检视，并增加了关键值打印。结果显示：

- 主键生成与写入逻辑未发现确定性错误；
- 异常路径中未发现可解释该问题的线程竞争；
- 异常位置与 Spark 内部 `Unsafe` 内存访问高度相关。

进一步排查发现，异常路径中存在多处最终调用 `Unsafe` 或 Spark 封装后的平台内存操作，例如：

- `Platform.copyMemory`
- `Platform.putLong`
- `Platform.getLong`
- 基于 `baseObject + baseOffset` 的结构解析
- 分配对象或数组后立即写入内部字段的代码路径

同时，不同 JDK 版本的表现存在明显差异：在较新的 JDK 版本中未观察到同类问题，而旧版 JDK 8 更容易触发。基于这一线索，排查方向从 Spark 业务逻辑收敛到 JDK 编译器优化差异。

最终，通过对相关 JDK patch 进行比对和验证，确认问题与 OpenJDK 缺陷 [JDK-8202414](https://bugs.openjdk.org/browse/JDK-8202414) 一致。

## JVM 层原因分析

### 触发模式

该缺陷主要发生在如下类型的代码模式中：

```java
byte[] buf = new byte[bufLen];
UNSAFE.putInt(buf, BYTE_ARRAY_BASE_OFFSET + 1, buf.length);
```

这里有几个关键点：

1. 先分配一个新的数组；
2. 数组刚创建后立刻通过 `Unsafe` 写入；
3. 写入地址不是自然对齐地址，例如 `BYTE_ARRAY_BASE_OFFSET + 1`；
4. 代码被 C2 编译优化，而不是解释执行。

解释执行时，对象分配、内存清零、后续写入是按顺序执行的，通常不会触发该问题。问题发生在 C2 优化后：编译器会尝试识别“新对象初始化后立即写入”的模式，并将对象创建、内存清零、字段或数组写入合并优化。

该优化逻辑涉及 HotSpot C2 中的对象初始化处理，例如 `PhaseMacroExpand::initialize_object`、`ClearArrayNode::clear_memory`、`InitializeNode::can_capture_store` 等路径。

### 错误发生点

C2 在优化对象初始化时，会尝试捕获紧跟在初始化之后的 `StoreNode`，并判断该 store 是否可以合并到初始化过程中。

问题在于，旧版本 JDK 对非对齐 `Unsafe` 写入的处理不够严格。对于某些 `Unsafe.putInt` / `Unsafe.putLong` 等非对齐写入，编译器错误地认为它们可以被安全捕获到初始化逻辑中。

换言之，旧版 C2 优化默认假设用户写入是对齐的，但实际应用代码可能通过 `Unsafe` 在 x86 等支持非对齐访问的平台上执行非对齐写入。一旦这个前提不成立，编译器就可能计算出错误的 store offset，进而在错误的位置执行清零。

### 一个简化例子

假设用户代码希望写入数组偏移区间 `[17, 21]`。由于非对齐访问处理错误，旧版 C2 可能错误计算出需要处理的相邻清零区间，并在 product build 中因为缺少断言保护而继续执行。

最终结果可能是：

- 数组头部或长度字段的部分字节被清零；
- 数组内容中的若干字节被意外写成 `0x00`；
- 后续读取到错误长度、错误地址或错误数据；
- 更严重时触发越界访问或 JVM 崩溃。

这也解释了为什么问题表现并不稳定：是否触发取决于代码是否被 C2 编译、访问是否非对齐、offset 是否落入敏感范围，以及被清零的位置是否会影响后续执行。

## 复现代码

下面的代码可用于理解该类问题的触发模式。实际是否复现取决于 JDK 版本、平台、编译阈值和运行参数。

```java
import sun.misc.Unsafe;

import java.lang.reflect.Field;
import java.security.AccessController;
import java.security.PrivilegedAction;

public class JvmTest {

  public static void main(String[] args) {
    System.err.close();
    int count = 0;
    while (count++ < 120000) {
      test();
    }
  }

  public static void test() {
    byte[] newBuf = serBytes(397);

    if (newBuf.length != 397) {
      System.out.println("array length internal error, expected: " +
              397 + " (0x" + Integer.toHexString(397) + ")"
              + " actual: " + newBuf.length
              + " (0x" + Integer.toHexString(newBuf.length) + ")");
    }
  }

  public static byte[] serBytes(int bufLen) {
    byte[] buf = new byte[bufLen];
    THE_UNSAFE.putInt(buf, BYTE_ARRAY_BASE_OFFSET + 1, buf.length);
    System.err.println("ref " + buf);
    return buf;
  }

  static final Unsafe THE_UNSAFE;
  static final long BYTE_ARRAY_BASE_OFFSET;

  static {
    THE_UNSAFE = (Unsafe) AccessController.doPrivileged(
            new PrivilegedAction<Object>() {
              @Override
              public Object run() {
                try {
                  Field f = Unsafe.class.getDeclaredField("theUnsafe");
                  f.setAccessible(true);
                  return f.get(null);
                } catch (NoSuchFieldException | IllegalAccessException e) {
                  throw new Error(e);
                }
              }
            }
    );
    BYTE_ARRAY_BASE_OFFSET = THE_UNSAFE.arrayBaseOffset(byte[].class);
  }
}
```

该例子的关键不是 `putInt` 本身，而是“新数组分配后立即进行非对齐 `Unsafe` 写入”这一模式。类似地，`putLong`、不同 offset、不同数组长度也可能触发相近行为。

## Spark 层影响分析

Spark 内部为了性能大量使用 `Unsafe` 和基于偏移的内存访问。典型模式包括：

```java
Platform.copyMemory(srcBase, srcOffset, dstBase, dstOffset, length);
```

以及类似：

```java
UnsafeRow row = new UnsafeRow(numFields);
row.pointTo(baseObject, baseOffset + offset, size);
```

或：

```java
long value = Platform.getLong(baseObject, baseOffset);
```

在正常情况下，这些操作是 Spark Tungsten 内存模型和高性能序列化的重要基础。但在旧版 JDK C2 缺陷存在时，只要某条路径满足“分配后立即写入 + 非对齐 Unsafe 访问 + 被 C2 捕获优化”的条件，就可能导致底层数组或结构体中的若干字节被错误清零。

因此，同一个 JVM 缺陷在 Spark 层可能表现为多种不同现象：

1. 如果被清零的是对象地址或偏移相关字段，可能表现为非法地址访问或 core dump；
2. 如果被清零的是长度或 size 字段，可能表现为地址截断、读取长度异常或数据截断；
3. 如果被清零的是普通数据字段，可能只表现为数据内容异常，不一定立即崩溃；
4. 如果错误位置暂时没有被后续逻辑读取，则可能完全无感知。

这也是该问题排查困难的主要原因：它不是稳定的业务逻辑错误，而是低概率、路径相关、编译状态相关的底层内存破坏。

## 为什么现象不稳定

该问题具备明显的偶发性，主要由以下因素共同决定：

1. **是否进入 C2 编译执行**  
   解释执行通常不会触发该优化路径，只有热点代码被 C2 编译后才可能暴露问题。

2. **是否存在非对齐 Unsafe 写入**  
   并非所有 `Unsafe` 写入都有风险；风险集中在非自然对齐的写入模式。

3. **offset 是否命中特定范围**  
   即使是非对齐写入，也需要 offset 落在特定位置，才会造成错误清零影响关键字段。

4. **被清零位置是否影响后续逻辑**  
   如果被污染的数据没有被读取，或者污染值没有改变控制流，问题可能不会显性暴露。

因此，core dump、地址截断、数据重复、字段变成零等不同现象，本质上可以由同一个编译器优化缺陷解释。

## 解决方案

### 方案一：升级 JDK

最推荐的方式是升级到已经包含 [JDK-8202414](https://bugs.openjdk.org/browse/JDK-8202414) 修复的 JDK 版本。

这是根治方案，因为它直接修复了 C2 对非对齐 store 捕获和初始化清零范围计算的问题。

### 方案二：规避非对齐 Unsafe 写入

如果短期无法升级 JDK，可以检查关键路径中是否存在类似以下模式：

```java
UNSAFE.putInt(array, BYTE_ARRAY_BASE_OFFSET + nonAlignedOffset, value);
UNSAFE.putLong(array, BYTE_ARRAY_BASE_OFFSET + nonAlignedOffset, value);
```

如果业务允许，可以改写为对齐写入，或通过普通数组访问、`ByteBuffer`、显式字节拆分等方式规避该优化触发条件。

该方式适合作为局部缓解，但不适合作为长期根治方案，因为 Spark 或依赖库内部仍可能存在类似模式。

### 方案三：禁用相关方法的 C2 编译

也可以通过 `-XX:CompileCommand` 对高风险方法进行解释执行或排除编译，例如：

```bash
-XX:CompileCommand=exclude,com/example/Foo.bar
```

该方案可以降低特定热点路径触发问题的概率，但需要准确定位相关方法，且可能带来性能损失。因此更适合作为临时止血措施，而不是最终解决方案。

## 总结

这次问题的核心经验是：当 Spark 这类高性能计算框架大量依赖 `Unsafe`、对象偏移和底层内存布局时，JVM 编译器缺陷可能以业务数据异常的形式暴露出来。

排查此类问题时，如果同时满足以下条件，应考虑从 JVM 编译器层面继续深入：

- 业务逻辑和并发路径无法解释异常；
- 异常表现为地址、长度、数组内容等底层数据结构损坏；
- 问题具有明显偶发性；
- 不同 JDK 版本表现存在差异；
- 相关路径大量使用 `Unsafe` 或直接内存访问；
- 问题只在热点运行一段时间后出现，冷启动或解释执行阶段不明显。

对于线上计算任务而言，JDK 版本不仅影响性能，也会影响底层内存语义的正确性。遇到类似低概率数据损坏问题时，除了排查业务逻辑、框架实现和并发竞争，也应将 JIT 编译器优化纳入根因分析范围。
