---
title: JDK 8/11 中 HttpURLConnection 抛出 "Network is unreachable" 的一次排查
date: 2024-05-27
categories:
  - jvm
tags:
  - jvm
  - jdk8
  - network
  - ipv6
  - troubleshooting
excerpt: IPv6-only 环境已设置 preferIPv6Addresses，连接仍报 Network is unreachable——根因竟是 JDK 把 fd 0 上的 Unix Domain Socket 误判为禁用 IPv6 的信号。
---

# JDK 8/11 中 HttpURLConnection 抛出 "Network is unreachable" 的一次排查

在一台仅启用 IPv6 的 Linux 主机上，Java 程序已经设置 `-Djava.net.preferIPv6Addresses=true`，访问 HTTPS 地址时却仍然抛出 `java.net.SocketException: Network is unreachable`。同一程序换到较新的 JDK 后恢复正常。

问题最终与 DNS、目标服务和 `HttpURLConnection` 本身都无关：**当标准输入（文件描述符 0）是 Unix Domain Socket 时，旧版 JDK 的 IPv6 探测逻辑可能错误地判定 IPv6 不可用。**

本文梳理复现现象、定位路径、源码根因以及版本修复策略。

## 1. 问题现象

测试环境具备以下特征：

- Linux 主机仅有 IPv6 网络连通性；
- Java 进程由另一个运行时通过子进程方式启动；
- Java 进程的文件描述符 0 连接到 Unix Domain Socket；
- JDK 8/11 运行失败，较新的 JDK 运行正常；
- JVM 参数中已包含 `-Djava.net.preferIPv6Addresses=true`。

最小测试程序如下：

```java
import java.net.HttpURLConnection;
import java.net.URL;

public class Main {
    public static void main(String[] args) throws Exception {
        System.err.println(
                "java.net.preferIPv6Addresses="
                        + System.getProperty("java.net.preferIPv6Addresses"));

        URL url = new URL("https://repo1.maven.org");
        HttpURLConnection connection =
                (HttpURLConnection) url.openConnection();
        connection.setConnectTimeout(10_000);
        connection.setReadTimeout(10_000);

        try {
            System.err.println("Response code: "
                    + connection.getResponseCode());
        } finally {
            connection.disconnect();
        }
    }
}
```

旧版 JDK 中的典型异常如下：

```text
Exception in thread "main" java.net.SocketException: Network is unreachable (connect failed)
    at java.net.PlainSocketImpl.socketConnect(Native Method)
    at java.net.AbstractPlainSocketImpl.doConnect(AbstractPlainSocketImpl.java:350)
    at java.net.AbstractPlainSocketImpl.connectToAddress(AbstractPlainSocketImpl.java:206)
    ...
    at sun.net.www.protocol.https.HttpsURLConnectionImpl.connect(HttpsURLConnectionImpl.java:153)
    at Main.main(Main.java:17)
```

## 2. 为什么 `preferIPv6Addresses` 没有解决问题

`java.net.preferIPv6Addresses` 主要影响地址解析结果的优先顺序。例如，在域名同时解析出 IPv4 和 IPv6 地址时，设置：

```bash
-Djava.net.preferIPv6Addresses=true
```

通常会让 IPv6 地址排在 `InetAddress.getAllByName()` 返回结果的前面，也会影响 `InetAddress.getByName()` 选择的首个地址。

但这个参数有一个前提：**JDK 必须先判定当前平台支持 IPv6。** 如果 JDK 在启动阶段已经把内部的“IPv6 可用”状态设置为 `false`，调整地址优先级并不能重新启用 IPv6。因此，参数已经生效但连接仍然失败时，应继续检查 JDK 的平台能力探测结果，而不是只围绕 DNS 顺序排查。

> `java.net.preferIPv6Addresses` 与 `java.net.preferIPv4Stack` 的语义不同。前者主要控制地址选择偏好；后者会影响协议栈选择。排查时不要混为一谈。

## 3. 验证 JDK 是否认为 IPv6 可用

在 JDK 8 中，可以通过反射调用内部接口，验证 `sun.nio.ch.Net.isIPv6Available()` 的结果：

```java
import java.lang.reflect.Method;

public class CheckIPv6 {
    public static void main(String[] args) throws Exception {
        Class<?> netClass = Class.forName("sun.nio.ch.Net");
        Method method = netClass.getDeclaredMethod("isIPv6Available");
        method.setAccessible(true);

        boolean available = (boolean) method.invoke(null);
        System.out.println("isIPv6Available=" + available);
    }
}
```

在问题环境中，该方法返回：

```text
isIPv6Available=false
```

这一步把问题范围从上层 HTTP/TLS 链路缩小到了 JDK 的本地网络初始化逻辑。

需要注意：这是诊断手段，不应作为业务代码依赖。`sun.nio.ch.Net` 属于 JDK 内部 API；在模块化 JDK 上，反射访问还可能需要额外的 `--add-opens` 参数。

## 4. 源码根因：文件描述符 0 被误判

旧版 Unix 网络实现中的 IPv6 探测逻辑包含类似代码：

```c
/*
 * If fd 0 is a socket it means we've been launched from inetd or
 * xinetd. If it's a socket then check the family - if it's an
 * IPv4 socket then we need to disable IPv6.
 */
if (getsockname(0, (struct sockaddr *)&sa, &sa_len) == 0) {
    struct sockaddr *saP = (struct sockaddr *)&sa;
    if (saP->sa_family != AF_INET6) {
        close(fd);
        return JNI_FALSE;
    }
}
```

这段逻辑原本是为了兼容由 `inetd`/`xinetd` 启动 Java 的场景：如果继承的标准输入是一个 IPv4 socket，JDK 会禁用 IPv6，以保持继承通道与其他 socket 的协议族一致。

问题在于判断条件过宽：

```c
saP->sa_family != AF_INET6
```

当文件描述符 0 是 Unix Domain Socket 时，地址族为 `AF_UNIX`。由于 `AF_UNIX != AF_INET6`，旧逻辑同样返回 `JNI_FALSE`，进而把整个 JVM 的 IPv6 能力标记为不可用。

因此，触发链路是：

1. 父进程启动 Java 子进程；
2. 子进程的文件描述符 0 连接到 Unix Domain Socket；
3. JDK 调用 `getsockname(0, ...)` 成功，得到 `AF_UNIX`；
4. 旧判断把所有非 `AF_INET6` 地址族都当成 IPv4 场景；
5. JVM 错误地禁用 IPv6；
6. 在 IPv6-only 环境中，网络连接最终报 `Network is unreachable`。

这里的 `close(fd)` 关闭的是 IPv6 探测过程中创建的临时 socket，而不是文件描述符 0；真正的问题是随后返回了 `JNI_FALSE`。

## 5. 上游修复

OpenJDK 问题 [JDK-8211842](https://bugs.openjdk.org/browse/JDK-8211842) 修正了这个判断。核心变化是只在文件描述符 0 明确属于 IPv4 时禁用 IPv6：

```c
if (getsockname(0, (struct sockaddr *)&sa, &sa_len) == 0) {
    if (sa.sa_family == AF_INET) {
        close(fd);
        return JNI_FALSE;
    }
}
```

修改后的语义更准确：

- `AF_INET`：继承的是 IPv4 socket，保留原有兼容行为；
- `AF_INET6`：IPv6 可继续使用；
- `AF_UNIX` 等其他地址族：不再被误判为“必须禁用 IPv6”。

该修复进入 JDK 12。对于仍需维护 JDK 8/11 的发行版，可以评估将该补丁回移到对应维护分支。

JDK 21 起，上游通过 [JDK-6914801](https://bugs.openjdk.org/browse/JDK-6914801) 进一步移除了启动阶段基于文件描述符 0 禁用 IPv6 的检查。对应 OpenJDK 提交可见：

- [JDK-8211842：修正 Unix Domain Socket 绑定 fd 0 时的 IPv6 误判](https://bugs.openjdk.org/browse/JDK-8211842)
- [JDK-6914801：移除相关协议族限制](https://bugs.openjdk.org/browse/JDK-6914801)
- [OpenJDK commit 8d17d1ee](https://github.com/openjdk/jdk/commit/8d17d1ee6f08ee90771d469182aaaaa7c23971fd)

## 6. 修复与规避策略

### 6.1 首选：升级到已修复的 JDK

优先使用包含 JDK-8211842 修复的 JDK，或使用已经完成等价回移的 JDK 8/11 发行版。验证时不要只看大版本号，还应确认具体更新版本或发行版补丁清单。

### 6.2 维护旧发行版：回移最小补丁

如果生产环境必须继续使用旧版 JDK 8/11，可回移 JDK-8211842 的最小修复，将“非 IPv6”判断收窄为“明确是 IPv4”。

回移时至少应覆盖以下测试矩阵：

| fd 0 类型 | 网络环境 | 预期结果 |
|---|---|---|
| 终端或普通管道 | IPv4/IPv6 双栈 | 行为不变 |
| IPv4 socket | 双栈 | 保留既有兼容行为 |
| IPv6 socket | IPv6 | IPv6 可用 |
| Unix Domain Socket | IPv6-only | 不应禁用 IPv6 |
| 关闭的 fd 0 | IPv6-only | 不应因该检查禁用 IPv6 |

### 6.3 临时规避：调整子进程的标准输入

如果暂时无法升级或修改 JDK，可以避免让 Java 子进程的文件描述符 0 指向 Unix Domain Socket，例如将标准输入重定向到 `/dev/null` 或普通管道。

这只是启动方式层面的规避，不应替代 JDK 修复。调整前还要确认应用不依赖标准输入或继承通道。

## 7. 排查清单

遇到 IPv6-only 环境中的 `Network is unreachable` 时，可以按以下顺序定位：

1. 确认主机是否实际配置 IPv6 地址和默认路由；
2. 检查目标域名的 AAAA 记录及网络连通性；
3. 确认 `java.net.preferIPv6Addresses` 的实际值；
4. 检查是否设置了 `java.net.preferIPv4Stack=true`；
5. 验证 JDK 内部是否认为 IPv6 可用；
6. 检查 `/proc/<pid>/fd/0` 指向的对象及其 socket 地址族；
7. 对比不同 JDK 更新版本的行为；
8. 核对所用发行版是否包含 JDK-8211842 或等价补丁。

在 Linux 上，可使用以下命令辅助确认文件描述符 0：

```bash
readlink /proc/<pid>/fd/0
```

如果需要进一步确认 socket 类型，可结合 `lsof`、`ss` 或调试器检查。不同容器和安全策略下，可见性可能受限。

## 8. 总结

这类故障容易被误判为 IPv6 地址排序问题，但真正的根因发生得更早：旧版 JDK 在初始化网络能力时，把文件描述符 0 上的 Unix Domain Socket 当成了不支持 IPv6 的信号。

关键经验有三点：

- JVM 参数只能影响其职责范围内的行为；地址偏好参数无法覆盖平台能力探测结果；
- 同一程序在不同 JDK 版本上的差异，是定位上游源码变更的重要线索；
- 进程启动方式和继承文件描述符也可能改变 JVM 的全局网络行为。

对于仍在维护 JDK 8/11 的环境，最稳妥的做法是确认发行版包含 JDK-8211842 的修复，并用 Unix Domain Socket 绑定 fd 0 的场景建立回归测试。