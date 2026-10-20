---
title: 从 Unsupported class file major version 21845 追查到 zlib 越界填充
date: 2022-09-26
categories:
  - jvm
tags:
  - java
  - zlib
  - asm
  - class-file
  - troubleshooting
  - native
excerpt: major version 21845 = 0x5555，一个不可能属于 Java 规范的数字，最终追到了 zlib 优化版在特定边界条件下把 padding 字节暴露给了调用方。
---

# 从 `Unsupported class file major version 21845` 追查到 zlib 越界填充

在 Java 生态中，`Unsupported class file major version` 通常意味着：当前使用的 ASM、Groovy 或构建工具不认识由更高版本 JDK 生成的 class 文件。

但如果报错中的 major version 是 **21845**，问题就没那么简单了。

21845 转换成十六进制恰好是 `0x5555`。它不对应任何合法的 Java class 文件版本，而是两个连续的 `0x55`。这个看似偶然的数字，最终将问题指向了底层解压库中的一段 padding 逻辑。

本文复盘一次跨越 Spring、ASM、Gradle、JDK 和 zlib 的故障排查过程，并总结这类问题的通用诊断方法。

## 1. 问题现象

某个 Spring 应用在启动阶段扫描 class 文件时失败，核心异常如下：

```text
org.springframework.core.NestedIOException:
ASM ClassReader failed to parse class file

Caused by: java.lang.IllegalArgumentException:
Unsupported class file major version 21845
```

类似问题也可能出现在 Gradle 构建阶段：

```text
BUG! exception in phase 'semantic analysis'
in source unit '_BuildScript_'
Unsupported class file major version 21845

Caused by: java.lang.IllegalArgumentException:
Unsupported class file major version 21845
    at groovyjarjarasm.asm.ClassReader.<init>(ClassReader.java:...)
```

共同点是：上层组件最终都通过 ASM 的 `ClassReader` 解析 class 文件，并认为自己读到了 major version 21845。

## 2. 为什么 21845 明显不正常

Java class 文件以 4 字节魔数开头：

```text
CA FE BA BE
```

紧随其后的是 minor version 和 major version，各占两个字节：

```text
u4 magic
u2 minor_version
u2 major_version
```

常见的 major version 包括：

| Java 版本 | Class major version |
|---|---:|
| Java 8 | 52 |
| Java 11 | 55 |
| Java 17 | 61 |
| Java 21 | 65 |

而：

```text
21845 = 0x5555
```

这意味着 ASM 解析 major version 时，读到的两个字节很可能都是 `0x55`。

因此，与其把它理解成“ASM 不支持某个未来版本的 Java”，不如先怀疑：

1. 输入流位置发生了偏移；
2. class 数据被截断或损坏；
3. 缓冲区中混入了固定填充值；
4. 底层解压实现返回了超出有效输出范围的数据。

这个数字本身就是非常关键的证据。

## 3. 为什么升级 Spring 能暂时绕过问题

问题首次出现时，触发点与 ASM 对 `InputStream` 的读取优化有关。

较新的 ASM 实现会尝试根据输入流可提供的数据量优化读取过程。Spring Framework 随后回退了相关调用方式，从而避免走到有问题的路径。升级到包含该调整的 Spring Framework 版本，可以让部分应用恢复运行。

相关修改：

- [Spring Framework workaround](https://github.com/spring-projects/spring-framework/commit/eabe946a5385b690228c1141bad3fc131ac7f1b3)
- [ASM InputStream optimization](https://gitlab.ow2.org/asm/asm/-/commit/cfda364ce57e39412b6cc89699b1003c6da6ec41)

但这只能算规避措施，而不是根因修复：

- 不只有 Spring 会使用 ASM；
- Gradle、Groovy、字节码增强工具等也可能读取同一类输入流；
- 只要上层读取方式触发该边界条件，错误就可能再次出现。

事实上，之后在 Gradle 构建中观察到的同类异常，证明问题并不局限于 Spring。

## 4. 将排查范围下沉到 zlib

出现问题的 JDK 构建使用了经过性能优化的 zlib 分支。与使用标准 zlib 的 JDK 对照后，可以观察到：

- 同一份工程和依赖，在标准 JDK 上构建正常；
- 更换为包含优化版 zlib 的 JDK 后，可稳定触发异常；
- Spring 和 Gradle 虽然调用链不同，但最终都从压缩归档中读取 class 文件；
- 异常版本号始终是具有明显填充特征的 `0x5555`。

这些现象把问题范围从 ASM 进一步缩小到 ZIP/JAR 解压链路。

> ASM 是第一个发现数据异常的组件，但并不是制造异常数据的组件。

## 5. 根因：空输出缓冲区被写入 `0x55`

先看 zlib `inflate` 路径中的几个关键变量：

- `in`：输入缓冲区，保存待解压的数据；
- `out`：输出缓冲区，保存解压后的数据；
- `have`：本轮实际产生的输出字节数；
- `left`：输出缓冲区中剩余的可用空间。

某些优化版 zlib 实现会在解压输出之后写入固定 padding，用于辅助调试或标识缓冲区边界，填充值恰好是 `0x55`。

问题发生在一个特殊边界条件下：本轮解压没有产生有效输出，输出指针仍位于缓冲区起始位置，但实现仍执行了 padding 写入。于是，调用方原本应当看到的“空输出”，被错误地表现为包含 `0x55` 的数据。

当上层代码继续把这段数据当作 class 文件读取时，两个连续的 `0x55` 被解释为 major version：

```text
major_version = (0x55 << 8) | 0x55
              = 0x5555
              = 21845
```

至此，异常数字、解压实现和 ASM 报错形成了完整证据链。

相关公开修复：

- [Chromium issue 1302606](https://bugs.chromium.org/p/chromium/issues/detail?id=1302606)
- [zlib-chromium fix](https://github.com/simonis/zlib-chromium/commit/424c27eb80718838d5ec38e00f91c9d584c98e30)
- [Chromium 后续调整：仅在 debug 场景写入 padding](https://chromium.googlesource.com/chromium/src/+/36be3c7a465f00f4edefccc10bba00bbebe1843d%5E%21/#F0)

修复的核心不是让 ASM 接受 21845，而是保证 zlib 只在满足边界条件时执行 padding，不能让填充值进入调用方可见的有效数据区域。

## 6. 为什么问题会表现为“偶发的上层兼容性故障”

这类问题难以定位，是因为错误跨越了多层组件：

```text
Spring / Gradle / Groovy
        ↓
       ASM
        ↓
 InputStream / ZIP stream
        ↓
   JDK native ZIP code
        ↓
       zlib
```

最终异常由 ASM 抛出，所以第一反应通常是 class 版本不兼容。但真正的数据破坏发生在更底层的解压阶段。

同时，问题是否出现还取决于上层读取模式：

- 一次读取多大的缓冲区；
- 是否依据 `available()` 或文件长度预分配空间；
- 是否在 EOF 附近继续发起读取；
- JAR 中目标 entry 的压缩布局；
- 是否触发“本轮无输出但仍执行收尾逻辑”的边界路径。

因此，同一个 JAR 可能被一种框架正常读取，却在另一种框架或另一个版本中失败。上层组件的升级可能改变触发条件，但并没有消除底层缺陷。

## 7. 一套更高效的排查方法

### 7.1 先验证错误值是否具有模式

看到异常数字时，不要只查版本对照表，先转换进制：

```bash
printf '0x%x\n' 21845
# 0x5555
```

如果结果是 `0x0000`、`0xffff`、`0x5555`、`0xaaaa` 或其他重复字节，应优先考虑：

- 内存初始化值；
- debug padding；
- poison pattern；
- 缓冲区越界或长度计算错误；
- EOF 处理错误。

### 7.2 区分“文件损坏”和“读取结果损坏”

可以对原始 JAR 做交叉验证：

```bash
unzip -p app.jar path/to/Target.class | xxd | head
```

正常 class 文件应以如下字节开头：

```text
ca fe ba be
```

如果磁盘上的 JAR 内容正确，但 Java 进程读出的数据错误，就应该重点检查运行时解压链路，而不是重新编译 class 文件。

### 7.3 做最小化环境对照

至少准备以下对照组：

1. 相同应用、相同 JAR，不同 JDK 构建；
2. 相同 JDK 主版本，标准 zlib 与优化版 zlib；
3. 相同 JDK，不同 Spring、ASM 或 Gradle 版本；
4. 相同输入，直接读取 class 与通过 `ZipInputStream`/`JarFile` 读取。

对照实验的目标不是立即找到补丁，而是确定错误发生在哪一层。

### 7.4 不要把 workaround 当作 root cause fix

如果升级框架后问题消失，需要继续回答：

- 新版本是修复了错误数据，还是仅改变了读取方式？
- 其他调用方是否仍可能触发？
- 同一个 native 库是否被 JDK 内多个模块复用？
- 是否存在静默数据损坏，而不仅仅是显式异常？

底层库违反 API 语义时，真正的修复通常应该落在底层。

## 8. 修复与验证建议

修复 zlib padding 边界后，建议至少覆盖以下测试：

### 8.1 功能回归

- Spring classpath 扫描；
- Gradle/Groovy 脚本编译；
- ASM 直接解析 JAR 中的 class；
- `JarFile`、`ZipFile`、`ZipInputStream` 等常见读取路径；
- 小文件、空文件和接近缓冲区边界的 entry。

### 8.2 边界测试

重点构造：

- 输出缓冲区刚好被填满；
- 本轮 `inflate` 没有产生输出；
- 解压刚好结束；
- 连续多次小缓冲区读取；
- EOF 前后重复读取；
- 不同压缩级别和 block 布局。

### 8.3 数据一致性验证

对解压前后的内容做哈希校验，确保修复不仅消除了异常，还没有造成静默数据变化：

```bash
unzip -p app.jar path/to/Target.class | sha256sum
```

也可以分别使用标准 JDK 与待验证 JDK 导出相同 entry，再比较二进制内容。

## 9. 总结

`Unsupported class file major version 21845` 表面上是 ASM 的版本检查失败，实际根因却可能是 zlib 在特定边界条件下把 `0x55` padding 暴露给了调用方。

这次问题最值得复用的经验有三点：

1. **异常值本身可能就是线索。** `21845 = 0x5555`，重复字节通常暗示填充或内存边界问题。
2. **报错组件不一定是故障组件。** ASM 只是忠实地解析了错误输入，真正的问题位于更底层的解压实现。
3. **绕过触发条件不等于修复根因。** Spring 的调整可以降低问题暴露概率，但只有修复 zlib 的 padding 边界，才能保护所有上层调用方。

当 Java 异常中出现明显超出规范范围、又带有固定字节模式的数值时，排查视角不应停留在 Java 层。沿着 I/O、压缩库和 native 实现继续向下追，往往才是找到根因的关键。

## 参考资料

- [The Java Virtual Machine Specification: The class File Format](https://docs.oracle.com/javase/specs/jvms/se21/html/jvms-4.html)
- [Java class file — Wikipedia](https://en.wikipedia.org/wiki/Java_class_file)
- [Java bytecode version table](https://javaalmanac.io/bytecode/versions/)
- [Spring Framework workaround](https://github.com/spring-projects/spring-framework/commit/eabe946a5385b690228c1141bad3fc131ac7f1b3)
- [ASM InputStream optimization](https://gitlab.ow2.org/asm/asm/-/commit/cfda364ce57e39412b6cc89699b1003c6da6ec41)
- [Chromium issue 1302606](https://bugs.chromium.org/p/chromium/issues/detail?id=1302606)
- [zlib-chromium fix](https://github.com/simonis/zlib-chromium/commit/424c27eb80718838d5ec38e00f91c9d584c98e30)
