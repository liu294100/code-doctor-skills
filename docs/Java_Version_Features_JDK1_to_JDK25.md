# Java 版本特性全景总览（JDK 1.0 ~ JDK 25）

> 📅 整理时间：2026年6月12日
> 📖 参考来源：[Wikipedia - Java version history](https://en.wikipedia.org/wiki/Java_version_history) | [Marco Behler - Java Versions and Features](https://www.marcobehler.com/guides/a-guide-to-java-versions-and-features) | [Oracle Official Release Notes](https://www.java.com/releases/)
>
> Content was rephrased for compliance with licensing restrictions.

---

## 📊 版本总览表

| 版本 | 代号 | 发布日期 | 类型 | 核心亮点 |
|------|------|----------|------|----------|
| JDK 1.0 | Oak | 1996-01-23 | - | Java 诞生，AWT、Applet、基础 I/O |
| JDK 1.1 | - | 1997-02-19 | - | 内部类、JDBC、RMI、JavaBeans、反射 |
| J2SE 1.2 | Playground | 1998-12-08 | - | Collections 框架、Swing、JIT 编译器 |
| J2SE 1.3 | Kestrel | 2000-05-08 | - | HotSpot JVM、JNDI、JavaSound |
| J2SE 1.4 | Merlin | 2002-02-06 | - | assert、正则表达式、NIO、日志 API |
| J2SE 5.0 | Tiger | 2004-09-30 | - | 泛型、注解、枚举、自动装箱、增强 for |
| Java SE 6 | Mustang | 2006-12-11 | - | 脚本引擎、JDBC 4.0、编译器 API |
| Java SE 7 | Dolphin | 2011-07-28 | - | try-with-resources、diamond `<>`、NIO.2 |
| Java SE 8 | Spider | 2014-03-18 | **LTS** | **Lambda、Stream API、Optional、Date/Time API** |
| Java SE 9 | - | 2017-09-21 | - | 模块系统(Jigsaw)、JShell、集合工厂方法 |
| Java SE 10 | - | 2018-03-20 | - | `var` 局部变量类型推断 |
| Java SE 11 | - | 2018-09-25 | **LTS** | **HTTP Client、String 增强、单文件运行** |
| Java SE 12 | - | 2019-03-19 | - | Switch 表达式(预览)、Shenandoah GC |
| Java SE 13 | - | 2019-09-17 | - | Text Blocks(预览)、ZGC 改进 |
| Java SE 14 | - | 2020-03-17 | - | Switch 表达式(正式)、Records(预览)、instanceof 模式匹配(预览) |
| Java SE 15 | - | 2020-09-15 | - | Text Blocks(正式)、Sealed Classes(预览)、ZGC/Shenandoah 正式 |
| Java SE 16 | - | 2021-03-16 | - | Records(正式)、instanceof 模式匹配(正式)、jpackage |
| Java SE 17 | - | 2021-09-14 | **LTS** | **Sealed Classes(正式)、switch 模式匹配(预览)** |
| Java SE 18 | - | 2022-03-22 | - | UTF-8 默认字符集、Simple Web Server |
| Java SE 19 | - | 2022-09-20 | - | Virtual Threads(预览)、Record Patterns(预览) |
| Java SE 20 | - | 2023-03-21 | - | Scoped Values(孵化)、多项预览继续迭代 |
| Java SE 21 | - | 2023-09-19 | **LTS** | **Virtual Threads(正式)、Pattern Matching for switch(正式)、Record Patterns(正式)、Sequenced Collections** |
| Java SE 22 | - | 2024-03-19 | - | Foreign Function & Memory API(正式)、Stream Gatherers(预览) |
| Java SE 23 | - | 2024-09-17 | - | Markdown 文档注释、Module Import(预览) |
| Java SE 24 | - | 2025-03-18 | - | Stream Gatherers(正式)、Class-File API(正式)、量子抗性加密 |
| Java SE 25 | - | 2025-09-16 | **LTS** | **Compact Source Files、Module Import(正式)、Flexible Constructor Bodies(正式)、Scoped Values(正式)、Compact Object Headers** |

> **LTS 版本时间线**：Java 8 → Java 11 → Java 17 → Java 21 → Java 25

---

## 📋 各版本详细特性

---

### JDK 1.0（1996年1月23日）

Java 语言第一个正式发布版本，Sun Microsystems 推出。

**核心特性：**
- 基础语言类型（`java.lang` 包）和工具类（`java.util` 包）
- AWT（Abstract Window Toolkit）图形框架
- Java Applet 支持（浏览器中运行 Java 程序）
- 基础 I/O 和网络库（`java.io`、`java.net`）
- 跨平台 JVM（"Write Once, Run Anywhere"）

---

### JDK 1.1（1997年2月19日）

**语言层面：**
- **内部类（Inner Classes）**：支持在类内部定义类
- **反射（Reflection）**：支持运行时自省（仅读取，不可修改）

**库和框架：**
- **JDBC**（Java Database Connectivity）：数据库连接标准
- **RMI**（Remote Method Invocation）：远程方法调用
- **JavaBeans**：组件模型规范
- **序列化（Serialization）**
- **国际化（i18n）** 和 Unicode 支持
- AWT 事件模型全面改造
- JIT 编译器（Windows 平台，Symantec 提供）

---

### J2SE 1.2（1998年12月8日）— 代号 Playground

这是一个里程碑式的发布，Java 平台大小增至 1520 个类、59 个包。从此版本起，Java 被重新品牌化为"Java 2"。

**核心新增：**
- **Collections Framework**：`List`、`Set`、`Map` 等集合框架
- **Swing** GUI 工具包整合到核心类库
- **JIT 编译器**正式集成到 Sun JVM
- `strictfp` 关键字（精确浮点运算）
- Java IDL / CORBA 互操作
- Java Plugin（浏览器插件）
- 反射增强：`AccessibleObject`，支持运行时修改对象

---

### J2SE 1.3（2000年5月8日）— 代号 Kestrel

**核心新增：**
- **HotSpot JVM**：高性能 JVM 成为默认（最初在 1.2 中作为独立下载）
- **JNDI**（Java Naming and Directory Interface）：纳入核心库
- **Java Platform Debugger Architecture (JPDA)**
- **JavaSound** API
- RMI 支持 CORBA 协议
- 合成代理类（Synthetic Proxy Classes）

> 最后一个支持 Windows 95 的 Java 版本

---

### J2SE 1.4（2002年2月6日）— 代号 Merlin

第一个通过 Java Community Process (JCP) 开发的版本。

**语言特性：**
- **`assert` 关键字**：断言机制

**库改进：**
- **正则表达式**（`java.util.regex`，参考 Perl 风格）
- **NIO**（Non-blocking I/O，`java.nio`）：高性能非阻塞 I/O
- **异常链（Exception Chaining）**
- **日志 API**（`java.util.logging`）
- **XML 解析器和 XSLT 处理器**（JAXP）
- **安全和加密扩展集成**（JCE、JSSE、JAAS）
- Image I/O API（JPEG、PNG 读写）
- IPv6 支持
- Java Web Start
- Preferences API（`java.util.prefs`）

---

### Java SE 5.0（2004年9月30日）— 代号 Tiger

**这是 Java 语言最重要的一次升级**，引入了大量现代编程语言特性。内部版本号仍为 1.5。

**语言特性（重大）：**

| 特性 | 说明 |
|------|------|
| **泛型（Generics）** | 编译期类型安全，消除强制转换 |
| **注解（Annotations）** | `@Override`、`@Deprecated` 等元数据标记 |
| **枚举（Enumerations）** | `enum` 关键字，类型安全的枚举 |
| **自动装箱/拆箱（Autoboxing）** | `int` ↔ `Integer` 自动转换 |
| **可变参数（Varargs）** | `void method(String... args)` |
| **增强 for 循环（for-each）** | `for (String s : list)` |
| **静态导入（Static Import）** | `import static` |

**库改进：**
- `java.util.concurrent` 并发工具包
- `Scanner` 类
- `StringBuilder`（非同步的 `StringBuffer` 替代）
- Java Memory Model 改进

```java
// 泛型示例
List<String> names = new ArrayList<String>();

// 增强 for 循环
for (String name : names) {
    System.out.println(name);
}

// 枚举
enum Season { SPRING, SUMMER, AUTUMN, WINTER }

// 注解
@Override
public String toString() { return "Hello"; }
```

---

### Java SE 6（2006年12月11日）— 代号 Mustang

从此版本起，"J2SE" 更名为 "Java SE"，版本号去掉了 ".0"。

**核心新增：**
- **脚本语言支持**（JSR 223）：内置 Rhino JavaScript 引擎
- **JDBC 4.0**
- **Java Compiler API**（JSR 199）：程序化调用编译器
- **可插拔注解处理**（JSR 269）
- JAXB 2.0 + StAX 解析器
- JAX-WS（Web Service）支持
- Swing 改进（SwingWorker、表格排序过滤、真双缓冲）
- JVM 性能大幅提升（同步优化、GC 升级、启动性能）

---

### Java SE 7（2011年7月28日）— 代号 Dolphin

经历了近 5 年的开发周期（Java 6 → Java 7），引入了 Project Coin 小型语言改进。

**语言特性（Project Coin）：**

| 特性 | 示例 |
|------|------|
| **switch 支持 String** | `switch(str) { case "hello": ... }` |
| **try-with-resources** | `try (InputStream is = ...) { }` |
| **钻石操作符 `<>`** | `List<String> list = new ArrayList<>()` |
| **multi-catch** | `catch (IOException \| SQLException e)` |
| **二进制字面量** | `int b = 0b1010_1010` |
| **数字下划线** | `int million = 1_000_000` |

**库和平台改进：**
- **NIO.2**（`java.nio.file`）：全新文件系统 API、符号链接、文件监视
- **Fork/Join 框架**（JSR 166）
- `invokedynamic` 字节码指令（为动态语言铺路）
- 椭圆曲线加密（ECC）
- Timsort 排序算法

```java
// try-with-resources
try (BufferedReader br = new BufferedReader(new FileReader("file.txt"))) {
    String line = br.readLine();
}

// 钻石操作符
Map<String, List<String>> map = new HashMap<>();

// multi-catch
try {
    // ...
} catch (IOException | SQLException e) {
    logger.error("Error", e);
}
```

---

### Java SE 8（2014年3月18日）🏆 LTS

**Java 历史上最具革命性的版本之一**，让 Java 进入函数式编程时代。

**语言特性（重大）：**

| 特性 | 说明 |
|------|------|
| **Lambda 表达式** | `(x, y) -> x + y` |
| **方法引用** | `String::toUpperCase` |
| **接口默认方法** | `default void method() { }` |
| **函数式接口** | `@FunctionalInterface` |
| **类型注解** | 注解可用于任何类型使用位置 |
| **重复注解** | 同一注解可多次应用 |

**核心 API 新增：**

| API | 说明 |
|-----|------|
| **Stream API** | 集合的函数式流处理 |
| **Optional** | 优雅处理 null |
| **Date and Time API** (`java.time`) | 取代 `Date`/`Calendar` |
| **CompletableFuture** | 异步编程 |
| **Nashorn** JavaScript 引擎 | 替代 Rhino |

**JVM 改进：**
- **永久代（PermGen）移除**，替换为 Metaspace
- 静态链接 JNI 库

```java
// Lambda + Stream API
List<String> names = Arrays.asList("franz", "ferdinand", "fiel");
names.stream()
    .filter(name -> name.startsWith("f"))
    .map(String::toUpperCase)
    .sorted()
    .forEach(System.out::println);

// Optional
Optional<String> opt = Optional.ofNullable(getValue());
String result = opt.orElse("default");

// Date/Time API
LocalDate today = LocalDate.now();
LocalDateTime dateTime = LocalDateTime.of(2024, Month.MARCH, 15, 10, 30);
Duration duration = Duration.between(start, end);
```

---

### Java SE 9（2017年9月21日）

从此版本开始，Java 切换到**每 6 个月一个版本**的发布节奏。

**核心特性：**

| 特性 | 说明 |
|------|------|
| **模块系统（Project Jigsaw / JPMS）** | `module-info.java`，JDK 自身模块化 |
| **JShell** | 交互式 REPL 工具 |
| **集合工厂方法** | `List.of()`、`Set.of()`、`Map.of()` |
| **接口私有方法** | `private void helper() { }` |
| **Compact Strings** | String 内部存储优化（Latin-1 用 byte[]） |
| **Reactive Streams** | `java.util.concurrent.Flow` |
| **jlink** | 自定义最小运行时镜像 |
| **Multi-release JAR** | 同一 JAR 包含多版本 class |
| **AOT 编译（实验性）** | 提前编译 |

```java
// 集合工厂方法
List<String> list = List.of("one", "two", "three");
Set<Integer> set = Set.of(1, 2, 3);
Map<String, Integer> map = Map.of("a", 1, "b", 2);

// Stream 增强
Stream.iterate("", s -> s + "s")
      .takeWhile(s -> s.length() < 10)
      .forEach(System.out::println);

// Optional 增强
optional.ifPresentOrElse(
    value -> System.out.println(value),
    () -> System.out.println("empty")
);

// 模块声明 (module-info.java)
module com.myapp {
    requires java.sql;
    exports com.myapp.api;
}
```

**重要移除：** JavaDB 从 JDK 中移除

---

### Java SE 10（2018年3月20日）

**核心特性：**

| 特性 | 说明 |
|------|------|
| **`var` 局部变量类型推断** | 编译器推断局部变量类型 |
| 应用程序类数据共享（AppCDS） | 加速启动 |
| G1 并行 Full GC | GC 性能改进 |
| 实验性 Java-Based JIT（Graal） | - |
| Root Certificates | CA 证书捆绑 |
| 时间基版本号方案 | 统一版本号格式 |

```java
// var 局部变量类型推断
var list = new ArrayList<String>();   // 推断为 ArrayList<String>
var stream = list.stream();           // 推断为 Stream<String>
var map = Map.of("key", "value");     // 推断为 Map<String, String>

// 注意：var 只能用于局部变量，不能用于字段、方法参数、返回类型
```

---

### Java SE 11（2018年9月25日）🏆 LTS

**核心新增：**

| 特性 | 说明 |
|------|------|
| **HTTP Client（正式版）** | 支持 HTTP/2、WebSocket |
| **String 增强方法** | `isBlank()`、`lines()`、`strip()`、`repeat()` |
| **Files 增强** | `readString()`、`writeString()` |
| **单文件源码运行** | `java HelloWorld.java` |
| **Lambda 参数的 var** | `(var x, var y) -> x + y` |
| **Epsilon GC** | No-Op 垃圾收集器 |
| **ZGC（实验性）** | 超低延迟 GC |
| **Flight Recorder** | 生产级性能诊断工具 |
| **TLS 1.3** | 安全通信协议升级 |
| **ChaCha20/Poly1305** | 新加密算法 |

**重要移除：**
- Java Applets
- Java Web Start
- JavaFX（独立项目）
- Java EE 模块（JAXB、JAX-WS 等）
- CORBA
- Nashorn 标记弃用

```java
// String 新方法
"  ".isBlank();                // true
"Hello\nWorld".lines().count(); // 2
"  Hello  ".strip();           // "Hello"
"Ha".repeat(3);                // "HaHaHa"

// HTTP Client
HttpClient client = HttpClient.newHttpClient();
HttpRequest request = HttpRequest.newBuilder()
    .uri(URI.create("https://api.example.com"))
    .build();
HttpResponse<String> response = client.send(request, 
    HttpResponse.BodyHandlers.ofString());

// 单文件运行
// $ java HelloWorld.java
```

---

### Java SE 12（2019年3月19日）

**核心特性：**
- **Switch 表达式（预览）**：箭头语法、`yield` 返回值
- **Shenandoah GC（实验性）**：低暂停时间 GC
- 微基准测试套件（JMH 集成）
- G1 优化：可中止混合收集、及时返回未使用内存

```java
// Switch 表达式 (Preview)
int numDays = switch (month) {
    case JAN, MAR, MAY, JUL, AUG, OCT, DEC -> 31;
    case APR, JUN, SEP, NOV -> 30;
    case FEB -> {
        if (year % 4 == 0) yield 29;
        else yield 28;
    }
};
```

---

### Java SE 13（2019年9月17日）

**核心特性：**
- **Text Blocks（预览）**：多行字符串字面量
- Switch 表达式（第二次预览）
- ZGC：归还未使用内存
- 动态 CDS 归档
- Socket API 重新实现

```java
// Text Blocks (Preview)
String html = """
        <html>
            <body>
                <p>Hello, World</p>
            </body>
        </html>
        """;

String query = """
        SELECT id, name, email
        FROM users
        WHERE active = true
        ORDER BY name
        """;
```

---

### Java SE 14（2020年3月17日）

**核心特性：**

| 特性 | 状态 |
|------|------|
| **Switch 表达式** | ✅ 正式 |
| **instanceof 模式匹配** | 预览 |
| **Records** | 预览 |
| **Helpful NullPointerExceptions** | ✅ 正式 |
| Text Blocks | 第二次预览 |
| jpackage | 孵化 |
| Foreign Memory Access | 孵化 |

**重要移除：** CMS 垃圾收集器

```java
// instanceof 模式匹配 (Preview)
if (obj instanceof String s) {
    System.out.println(s.length()); // 无需强转
}

// Records (Preview)
record Point(int x, int y) { }
Point p = new Point(3, 4);
System.out.println(p.x()); // 3

// Helpful NullPointerException
// 以前: NullPointerException
// 现在: Cannot invoke "String.length()" because "user.getName()" is null
```

---

### Java SE 15（2020年9月15日）

**核心特性：**

| 特性 | 状态 |
|------|------|
| **Text Blocks** | ✅ 正式 |
| **Sealed Classes** | 预览 |
| **ZGC** | ✅ 正式（生产可用） |
| **Shenandoah GC** | ✅ 正式（生产可用） |
| Hidden Classes | ✅ 正式 |
| Records | 第二次预览 |
| instanceof 模式匹配 | 第二次预览 |
| EdDSA 签名算法 | ✅ 正式 |

**重要移除：** Nashorn JavaScript 引擎、Solaris/SPARC 端口

```java
// Sealed Classes (Preview)
public abstract sealed class Shape
    permits Circle, Rectangle, Square { }

public final class Circle extends Shape { }
public final class Rectangle extends Shape { }
public non-sealed class Square extends Shape { } // 允许进一步继承
```

---

### Java SE 16（2021年3月16日）

**核心特性：**

| 特性 | 状态 |
|------|------|
| **Records** | ✅ 正式 |
| **instanceof 模式匹配** | ✅ 正式 |
| **jpackage** | ✅ 正式（打包分发工具） |
| Sealed Classes | 第二次预览 |
| Vector API | 孵化 |
| Foreign Linker API | 孵化 |
| Unix-Domain Socket | ✅ 正式 |
| Elastic Metaspace | ✅ 正式 |

**里程碑：** OpenJDK 源码从 Mercurial 迁移到 GitHub

```java
// Records (正式)
public record User(long id, String name, String email) {
    // 自动生成 constructor, getters, equals(), hashCode(), toString()
    
    // 紧凑构造器（校验）
    public User {
        if (name == null || name.isBlank()) {
            throw new IllegalArgumentException("Name required");
        }
    }
}

// instanceof 模式匹配 (正式)
if (obj instanceof User user && user.id() > 0) {
    processUser(user);
}
```

---

### Java SE 17（2021年9月14日）🏆 LTS

**核心特性：**

| 特性 | 状态 |
|------|------|
| **Sealed Classes** | ✅ 正式 |
| **Pattern Matching for switch** | 预览 |
| 恢复严格浮点语义 | ✅ 正式 |
| 增强伪随机数生成器 | ✅ 正式 |
| macOS/AArch64 端口 | ✅ 正式 |
| Foreign Function & Memory API | 孵化 |
| Vector API | 第二次孵化 |
| 上下文特定反序列化过滤器 | ✅ 正式 |

**重要移除/弃用：**
- 移除 RMI Activation
- 移除实验性 AOT 和 Graal JIT 编译器
- 弃用 Security Manager
- 弃用 Applet API
- `strictfp` 关键字变为无效（始终严格）

```java
// Sealed Classes (正式)
public sealed interface Payment permits CreditCard, WireTransfer, Crypto { }
public record CreditCard(String number, YearMonth expiry) implements Payment { }
public record WireTransfer(String iban) implements Payment { }
public final class Crypto implements Payment { /* ... */ }

// Pattern Matching for switch (Preview)
Object obj = getPayment();
String result = switch (obj) {
    case null           -> "null";
    case String s       -> "String: " + s;
    case Integer i      -> "Integer: " + i;
    case CreditCard cc  -> "Card: " + cc.number();
    default             -> "Unknown";
};
```

---

### Java SE 18（2022年3月22日）

**核心特性：**

| 特性 | 说明 |
|------|------|
| **UTF-8 默认字符集** | 所有平台统一 UTF-8 |
| **Simple Web Server** | `jwebserver` 命令，用于开发测试 |
| **Javadoc 代码片段** | `@snippet` 标签 |
| 方法句柄重新实现核心反射 | 性能改进 |
| Internet-Address Resolution SPI | DNS 解析可定制 |
| Finalization 弃用 | 标记为将来移除 |
| Pattern Matching for switch | 第二次预览 |
| Foreign Function & Memory API | 第二次孵化 |
| Vector API | 第三次孵化 |

---

### Java SE 19（2022年9月20日）

**核心特性：**

| 特性 | 状态 |
|------|------|
| **Virtual Threads** | 预览 ⭐ |
| **Record Patterns** | 预览 |
| **Structured Concurrency** | 孵化 |
| Pattern Matching for switch | 第三次预览 |
| Foreign Function & Memory API | 预览 |
| Vector API | 第四次孵化 |
| Linux/RISC-V 端口 | ✅ 正式 |

```java
// Virtual Threads (Preview) - 轻量级线程
Thread.startVirtualThread(() -> {
    System.out.println("Running in virtual thread");
});

// Record Patterns (Preview)
record Point(int x, int y) { }
if (obj instanceof Point(int x, int y)) {
    System.out.println(x + y);
}
```

---

### Java SE 20（2023年3月21日）

所有 JEP 均为预览或孵化阶段：

| 特性 | 状态 |
|------|------|
| Scoped Values | 孵化 |
| Record Patterns | 第二次预览 |
| Pattern Matching for switch | 第四次预览 |
| Foreign Function & Memory API | 第二次预览 |
| Virtual Threads | 第二次预览 |
| Structured Concurrency | 第二次孵化 |
| Vector API | 第五次孵化 |

---

### Java SE 21（2023年9月19日）🏆 LTS

**这是自 Java 8 以来最重要的 LTS 版本**，多个长期预览的特性正式毕业。

**正式特性（Final）：**

| 特性 | 说明 |
|------|------|
| **Virtual Threads** | 百万级轻量线程，颠覆并发模型 |
| **Pattern Matching for switch** | 完整模式匹配 |
| **Record Patterns** | 解构记录类型 |
| **Sequenced Collections** | `SequencedCollection`/`SequencedMap` |
| **Generational ZGC** | 分代 ZGC 提升性能 |
| **Key Encapsulation Mechanism API** | 量子安全密钥封装 |

**预览/孵化：**
- String Templates（预览）
- Unnamed Patterns and Variables（预览）
- Unnamed Classes and Instance Main Methods（预览）
- Scoped Values（预览）
- Structured Concurrency（预览）
- Vector API（第六次孵化）

```java
// Virtual Threads (正式)
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    IntStream.range(0, 10_000).forEach(i -> {
        executor.submit(() -> {
            Thread.sleep(Duration.ofSeconds(1));
            return i;
        });
    });
}

// Pattern Matching for switch (正式) + Record Patterns
sealed interface Shape permits Circle, Rectangle { }
record Circle(double radius) implements Shape { }
record Rectangle(double w, double h) implements Shape { }

double area = switch (shape) {
    case Circle(var r)        -> Math.PI * r * r;
    case Rectangle(var w, var h) -> w * h;
};

// Sequenced Collections
SequencedCollection<String> list = new ArrayList<>();
list.addFirst("first");
list.addLast("last");
String first = list.getFirst();
String last = list.getLast();
list.reversed().forEach(System.out::println);
```

---

### Java SE 22（2024年3月19日）

**核心特性：**

| 特性 | 状态 |
|------|------|
| **Foreign Function & Memory API** | ✅ 正式 |
| **Unnamed Variables & Patterns** | ✅ 正式 |
| Region Pinning for G1 | ✅ 正式 |
| Multi-File Source-Code Programs | ✅ 正式 |
| Stream Gatherers | 预览 |
| Statements before super(...) | 预览 |
| Class-File API | 预览 |
| String Templates | 第二次预览 |
| Structured Concurrency | 第二次预览 |
| Scoped Values | 第二次预览 |
| Vector API | 第七次孵化 |

```java
// Foreign Function & Memory API (正式)
try (Arena arena = Arena.ofConfined()) {
    MemorySegment segment = arena.allocate(100);
    segment.set(ValueLayout.JAVA_INT, 0, 42);
    int value = segment.get(ValueLayout.JAVA_INT, 0);
}

// Unnamed Variables
if (obj instanceof Point(int x, _)) {
    // 只关心 x，忽略 y
    System.out.println(x);
}

try {
    // ...
} catch (Exception _) {
    // 不需要使用异常变量
    log.error("Something failed");
}
```

---

### Java SE 23（2024年9月17日）

**核心特性：**

| 特性 | 状态 |
|------|------|
| **Markdown 文档注释** | ✅ 正式 |
| **ZGC 分代模式默认开启** | ✅ 正式 |
| Primitive Types in Patterns/switch | 预览 |
| Class-File API | 第二次预览 |
| Stream Gatherers | 第二次预览 |
| Module Import Declarations | 预览 |
| Flexible Constructor Bodies | 第二次预览 |
| Structured Concurrency | 第三次预览 |
| Scoped Values | 第三次预览 |
| Vector API | 第八次孵化 |
| 弃用 sun.misc.Unsafe 内存方法 | - |

**注意：** String Templates 在 Java 23 中被移除（设计问题）

```java
/// Markdown 文档注释示例
///
/// Finds an active user by their ID.
///
/// @param id the user identifier
/// @return the user wrapped in Optional
Optional<User> findUser(long id) {
    return repository.findById(id);
}
```

---

### Java SE 24（2025年3月18日）

24 个 JEP 的大版本：

**正式特性（Final）：**

| 特性 | 说明 |
|------|------|
| **Stream Gatherers** | 自定义中间操作 |
| **Class-File API** | 读写和转换 .class 文件 |
| **永久禁用 Security Manager** | 不可再启用 |
| **ZGC 移除非分代模式** | 仅保留分代 ZGC |
| **Quantum-Resistant 加密** | ML-KEM + ML-DSA（后量子） |
| AOT Class Loading & Linking | 加速启动 |
| Virtual Thread 同步改进 | synchronized 不再 pin 虚拟线程 |
| Linking Run-Time Images without JMODs | - |

**重要移除：** Windows 32-bit x86 端口移除

```java
// Stream Gatherers (正式)
var result = orders.stream()
    .gather(Gatherers.windowFixed(3))  // 每3个元素一组
    .toList();

// 滑动窗口
var sliding = numbers.stream()
    .gather(Gatherers.windowSliding(5))
    .toList();
```

---

### Java SE 25（2025年9月16日）🏆 LTS

**当前最新 LTS 版本**。

**正式特性（Final）：**

| 特性 | 说明 |
|------|------|
| **Compact Source Files & Instance Main Methods** | 简化入口类 |
| **Module Import Declarations** | `module import java.base;` |
| **Flexible Constructor Bodies** | super() 前可执行语句 |
| **Scoped Values** | 替代 ThreadLocal 的安全替代品 |
| **Compact Object Headers** | 对象头从 128→64 位 |
| **Generational Shenandoah** | 分代 Shenandoah GC |
| **Key Derivation Function API** | 密钥派生标准 API |
| AOT Method Profiling | 加速预热 |
| AOT Command-Line Ergonomics | 简化 AOT 使用 |
| JFR CPU-Time Profiling（实验性） | - |
| JFR Cooperative Sampling | - |
| JFR Method Timing & Tracing | - |

**继续预览/孵化：**
- Primitive Types in Patterns/instanceof/switch（第三次预览）
- PEM Encodings of Cryptographic Objects（预览）
- Stable Values（预览）
- Structured Concurrency（第五次预览）
- Vector API（第十次孵化）

**重要移除：** 32-bit x86 端口完全移除

```java
// Compact Source Files - 不再需要 public class + public static void main
void main() {
    IO.println("Hello from a compact source file!");
}

// Module Import Declarations (正式)
module import java.base;

void main() {
    List<String> names = List.of("Java", "25", "LTS");
    IO.println(names);
}

// Flexible Constructor Bodies (正式)
class User {
    private final String email;

    User(String email) {
        // super() 之前可以执行验证逻辑
        if (!email.contains("@")) {
            throw new IllegalArgumentException("Invalid email: " + email);
        }
        super(); // 可以后调用
        this.email = email;
    }
}

// Scoped Values (正式) - 替代 ThreadLocal
private static final ScopedValue<User> CURRENT_USER = ScopedValue.newInstance();

ScopedValue.where(CURRENT_USER, authenticatedUser)
    .run(() -> {
        // 在这个作用域内可以读取
        User user = CURRENT_USER.get();
        processRequest(user);
    });
```

---

## 🔄 特性演进时间线（预览 → 正式）

重要特性从首次预览到正式发布的演进过程：

| 特性 | 首次预览 | 正式发布 | 迭代次数 |
|------|---------|---------|---------|
| Switch 表达式 | Java 12 | Java 14 | 3 |
| Text Blocks | Java 13 | Java 15 | 3 |
| Records | Java 14 | Java 16 | 3 |
| instanceof 模式匹配 | Java 14 | Java 16 | 3 |
| Sealed Classes | Java 15 | Java 17 | 3 |
| Pattern Matching for switch | Java 17 | Java 21 | 5 |
| Record Patterns | Java 19 | Java 21 | 3 |
| Virtual Threads | Java 19 | Java 21 | 3 |
| Foreign Function & Memory API | Java 19 | Java 22 | 4 |
| Stream Gatherers | Java 22 | Java 24 | 3 |
| Scoped Values | Java 20(孵化) | Java 25 | 6 |
| Module Import Declarations | Java 23 | Java 25 | 3 |
| Flexible Constructor Bodies | Java 22 | Java 25 | 4 |
| Structured Concurrency | Java 19(孵化) | 仍在预览(Java 25) | 7+ |
| Vector API | Java 16(孵化) | 仍在孵化(Java 25) | 10+ |

---

## 🗑️ 重要移除时间线

| 移除项 | 弃用版本 | 移除版本 | 说明 |
|--------|---------|---------|------|
| Java Applets | Java 9 | Java 11 | 浏览器嵌入式 Java |
| Java Web Start | Java 9 | Java 11 | JNLP 启动 |
| JavaFX | Java 11 | Java 11 | 独立为 OpenJFX |
| Java EE 模块 | Java 9 | Java 11 | 迁移到 Jakarta EE |
| CORBA | Java 9 | Java 11 | - |
| Nashorn JS 引擎 | Java 11 | Java 15 | 使用 GraalVM JS |
| CMS GC | Java 9 | Java 14 | 使用 G1/ZGC/Shenandoah |
| Solaris/SPARC 端口 | Java 14 | Java 15 | - |
| RMI Activation | Java 15 | Java 17 | - |
| AOT/Graal JIT | Java 16 | Java 16 | GraalVM 独立提供 |
| Security Manager | Java 17 | Java 24(永久禁用) | 设计过时 |
| Windows 32-bit x86 | Java 21 | Java 25 | - |
| Applet API | Java 17(弃用) | Java 26 | 最终清理 |

---

## 🏗️ GC 演进总结

| 垃圾收集器 | 引入版本 | 正式版本 | 特点 |
|-----------|---------|---------|------|
| Serial GC | JDK 1.0 | - | 单线程，客户端模式 |
| Parallel GC | J2SE 1.4 | - | 多线程，吞吐量优先 |
| CMS | J2SE 1.4 | - | 低暂停（Java 14 移除） |
| G1 | Java 7u4 | Java 9(默认) | 分区、可预测暂停 |
| ZGC | Java 11(实验) | Java 15 | 亚毫秒暂停、TB 级堆 |
| Shenandoah | Java 12(实验) | Java 15 | 并发压缩、低暂停 |
| Epsilon | Java 11 | Java 11 | 不回收（测试/短命进程） |
| Generational ZGC | Java 21 | Java 21 | 分代 ZGC |
| Generational Shenandoah | Java 24(实验) | Java 25 | 分代 Shenandoah |

---

## 💡 版本选择建议

### 企业项目推荐

| 场景 | 推荐版本 | 原因 |
|------|---------|------|
| 新项目（2025+） | **Java 21** 或 **Java 25** | LTS，Virtual Threads，现代特性齐全 |
| 存量项目迁移 | **Java 17** → **Java 21** | 渐进升级，17 是安全的中间站 |
| 遗留系统维护 | **Java 8** / **Java 11** | 仍在支持期，但应规划迁移 |
| 微服务/云原生 | **Java 21+** | Virtual Threads 大幅提升并发性能 |
| 高性能/低延迟 | **Java 25** | Compact Headers + AOT + 最新 GC |

### JDK 发行版选择

| 发行版 | 适用场景 |
|--------|---------|
| [Eclipse Temurin (Adoptium)](https://adoptium.net/) | 通用推荐，免费，多平台 |
| [Amazon Corretto](https://aws.amazon.com/corretto/) | AWS 环境 |
| [Azul Zulu](https://www.azul.com/downloads/) | 需要商业支持 |
| [GraalVM](https://www.graalvm.org/) | 需要原生编译/多语言 |
| [Oracle JDK](https://www.oracle.com/java/) | Oracle 客户/商业支持 |
| Red Hat OpenJDK | RHEL 环境 |

---

## 📚 参考资源

| 资源 | 链接 |
|------|------|
| OpenJDK 官方 | https://openjdk.org/ |
| Oracle Java SE 路线图 | https://www.oracle.com/java/technologies/java-se-support-roadmap.html |
| Java Almanac（版本对比） | https://javaalmanac.io/ |
| JEP 索引 | https://openjdk.org/jeps/0 |
| Java 发布列表 | https://www.java.com/releases/ |
| Marco Behler 版本指南 | https://www.marcobehler.com/guides/a-guide-to-java-versions-and-features |
| Wikipedia Java 版本历史 | https://en.wikipedia.org/wiki/Java_version_history |
| Adoptium 下载 | https://adoptium.net/ |
