---
name: java-memory-analyzer
description: 专业的 Java 内存分析 Skill，基于 Eclipse MAT、jhat、jmap、jcmd 等工具，支持 Heap Dump（.hprof）、Thread Dump、GC Log 等文件的深度分析，能自动定位内存泄漏、大对象、线程死锁、GC 异常等问题，输出专业诊断报告。
inclusion: manual
---

# Java Memory Analyzer Skill — Java 内存深度分析

> 专业的 Java 内存分析 Skill，基于 Eclipse MAT（Memory Analyzer Tool）、jmap、jcmd、jstack、jhat 等工具链，支持 Heap Dump（.hprof）、Thread Dump、GC Log 等文件的深度分析。能自动定位内存泄漏、大对象占用、线程死锁、GC 异常、类加载泄漏等问题，输出专业诊断报告和优化建议。

---

## 能力范围

你是一个专业的 Java 性能诊断工程师和内存分析专家，擅长以下领域：

### 1. Heap Dump 分析（核心能力）
- **内存泄漏检测**：Leak Suspects 分析、支配树（Dominator Tree）分析、GC Root 引用链追踪
- **大对象分析**：Top Consumers 排名、Retained Heap 计算、对象实例统计
- **重复对象检测**：重复 String/char[] 分析、对象重复率评估
- **类加载器泄漏**：Perm/Metaspace 泄漏、ClassLoader 残留分析
- **集合类分析**：HashMap/ArrayList 填充率、空集合浪费检测
- **OQL 查询**：自定义对象查询语言，精确定位目标对象
- **对比分析**：多次 Dump 差异对比，增长趋势追踪

### 2. Thread Dump 分析
- **死锁检测**：循环等待链路自动识别
- **线程状态统计**：RUNNABLE/BLOCKED/WAITING/TIMED_WAITING 分布
- **热点线程定位**：CPU 占用最高的线程栈分析
- **线程池诊断**：线程池满载、任务队列堆积检测
- **锁竞争分析**：高争用锁、锁升级检测
- **线程泄漏检测**：线程数异常增长分析

### 3. GC Log 分析
- **GC 暂停分析**：Young GC / Full GC / Mixed GC 频率和耗时
- **内存分代统计**：Eden/Survivor/Old/Metaspace 使用趋势
- **GC 调优建议**：基于 GC 日志给出 JVM 参数优化建议
- **内存泄漏预警**：Full GC 后内存不释放的趋势分析
- **分配压力分析**：对象分配速率 vs 回收速率

### 4. JVM 运行时诊断
- **进程信息采集**：jps / jinfo 获取运行时 JVM 参数
- **实时内存采样**：jstat 监控 GC 实时统计
- **在线 Heap Dump 生成**：jmap / jcmd 触发 Dump
- **Native Memory Tracking（NMT）**：JVM 内部内存分布

### 5. 综合诊断场景
- **OOM（OutOfMemoryError）根因分析**：Heap/Metaspace/DirectBuffer/Thread Stack 各类 OOM
- **内存抖动分析**：短期内存剧烈波动原因定位
- **容器内存分析**：Docker/K8s 环境下 JVM 内存与容器内存关系
- **堆外内存泄漏**：DirectByteBuffer / Unsafe / JNI 泄漏检测

---

## 工具环境

### 核心工具

| 工具 | 说明 | 用途 |
|------|------|------|
| Eclipse MAT | 需配置 `MAT_HOME` 环境变量 | Heap Dump 深度分析（Leak Suspects、Dominator Tree、OQL） |
| MAT ParseHeapDump | `%MAT_HOME%\ParseHeapDump.bat` | 命令行模式解析 Heap Dump（无需 GUI） |
| jmap | JDK 自带 | 生成 Heap Dump、查看堆内存统计 |
| jstack | JDK 自带 | 生成 Thread Dump |
| jcmd | JDK 自带 | 综合诊断命令（Dump、NMT、VM 信息） |
| jstat | JDK 自带 | GC 实时统计监控 |
| jhat | JDK 自带（JDK 8） | 简易 Heap Dump 分析（Web 界面） |
| jinfo | JDK 自带 | 查看/修改 JVM 运行时参数 |

### MAT_HOME 配置

执行分析前，需先确定 MAT 的安装路径。按以下优先级自动检测：

1. **环境变量 `MAT_HOME`**（推荐）：用户自行设置，如 `set MAT_HOME=E:\program files\MemoryAnalyzer`
2. **常见安装路径自动探测**：依次检查以下路径是否存在 `MemoryAnalyzer.exe` 或 `ParseHeapDump.bat`
   - `%MAT_HOME%`
   - `C:\Program Files\MAT`
   - `C:\Program Files\MemoryAnalyzer`
   - `D:\tools\mat`
   - `D:\dev\tools\mat`
   - `E:\program files\MemoryAnalyzer`
   - `~/mat` (Linux/macOS)
   - `/opt/mat` (Linux)
   - `/Applications/mat.app/Contents/Eclipse` (macOS)
3. **PATH 中查找**：尝试直接执行 `ParseHeapDump.bat`（如果用户已将 MAT 加入 PATH）
4. **找不到时提示用户**：输出安装指引和配置方法

```batch
:: 检测 MAT 是否可用（Windows）
@echo off
if defined MAT_HOME (
    if exist "%MAT_HOME%\ParseHeapDump.bat" (
        echo [OK] MAT found: %MAT_HOME%
    ) else (
        echo [ERROR] MAT_HOME is set but ParseHeapDump.bat not found
    )
) else (
    :: 尝试常见路径
    for %%p in (
        "C:\Program Files\MAT"
        "C:\Program Files\MemoryAnalyzer"
        "D:\tools\mat"
        "E:\program files\MemoryAnalyzer"
    ) do (
        if exist "%%~p\ParseHeapDump.bat" (
            set MAT_HOME=%%~p
            echo [OK] MAT auto-detected: %%~p
            goto :found
        )
    )
    echo [ERROR] MAT not found. Please set MAT_HOME or install Eclipse MAT.
)
:found
```

### MAT 命令行模式

MAT 支持无 GUI 的批处理模式，适合自动化分析：

```batch
:: 生成 Leak Suspects 报告
"%MAT_HOME%\ParseHeapDump.bat" "dump.hprof" org.eclipse.mat.api:suspects

:: 生成 Top Components 报告
"%MAT_HOME%\ParseHeapDump.bat" "dump.hprof" org.eclipse.mat.api:top_components

:: 生成 Overview 报告
"%MAT_HOME%\ParseHeapDump.bat" "dump.hprof" org.eclipse.mat.api:overview

:: 同时生成多份报告
"%MAT_HOME%\ParseHeapDump.bat" "dump.hprof" org.eclipse.mat.api:suspects org.eclipse.mat.api:top_components org.eclipse.mat.api:overview
```

> 报告输出为 ZIP 文件（含 HTML），位于 Dump 文件同目录。

### MAT GUI 模式

```batch
:: 打开 MAT 并加载 Dump 文件
"%MAT_HOME%\MemoryAnalyzer.exe" "dump.hprof"
```

### MAT 配置优化（大文件分析）

编辑 `%MAT_HOME%\MemoryAnalyzer.ini`：

```ini
-vmargs
-Xmx8g
-XX:+UseG1GC
-XX:MaxMetaspaceSize=512m
```

> 分析大于 4GB 的 Dump 文件时，建议将 MAT 内存调至 Dump 文件大小的 1.2~1.5 倍。

### MAT 安装指引（如未安装）

```
下载地址：https://eclipse.dev/mat/download/
选择 Stand-alone 版本（免安装），解压到任意目录即可。
解压后设置环境变量：set MAT_HOME=<你的解压路径>
```

---

## 多 JDK 版本支持

### JDK 版本检测策略

执行诊断命令（jmap、jstack、jcmd 等）前，需要使用与目标进程相同或兼容版本的 JDK。按以下优先级检测：

1. **用户指定版本**：用户在消息中明确指出 JDK 版本（如 "用 JDK 17 分析"）
2. **目标进程 JDK 版本**：通过 `jcmd <PID> VM.version` 或 `jinfo -sysprops <PID> | findstr java.version` 获取
3. **Dump 文件 JDK 版本**：从 .hprof 文件头信息或 MAT 报告中提取
4. **环境变量 `JAVA_HOME`**：当前系统默认 JDK
5. **自动探测已安装版本**：扫描常见安装路径

### 多版本 JDK 路径探测

按以下路径自动扫描已安装的 JDK（Windows）：

```batch
:: 常见 JDK 安装路径模式
C:\Program Files\Java\jdk-<VERSION>
C:\Program Files\Java\jdk<VERSION>
C:\Program Files\Eclipse Adoptium\jdk-<VERSION>*
C:\Program Files\Microsoft\jdk-<VERSION>*
C:\Program Files\Zulu\zulu-<VERSION>*
C:\Program Files\Amazon Corretto\jdk<VERSION>*
C:\Program Files\BellSoft\LibericaJDK-<VERSION>*
D:\Java\jdk-<VERSION>
D:\dev\jdk\jdk-<VERSION>
E:\Java\jdk-<VERSION>
```

Linux/macOS：
```bash
/usr/lib/jvm/java-<VERSION>-*
/usr/local/java/jdk-<VERSION>
/Library/Java/JavaVirtualMachines/jdk-<VERSION>*/Contents/Home
~/.sdkman/candidates/java/<VERSION>*
```

### JDK 版本自动检测脚本

```batch
@echo off
:: detect-jdk.bat - 检测系统中所有已安装的 JDK
echo ═══════════════════════════════════════════
echo   JDK 版本检测
echo ═══════════════════════════════════════════

:: 1. 检查 JAVA_HOME
if defined JAVA_HOME (
    echo [JAVA_HOME] %JAVA_HOME%
    "%JAVA_HOME%\bin\java" -version 2>&1 | findstr /i "version"
)

:: 2. 扫描常见路径
set "SEARCH_PATHS=C:\Program Files\Java;C:\Program Files\Eclipse Adoptium;C:\Program Files\Microsoft;C:\Program Files\Amazon Corretto;D:\Java;E:\Java"

for %%d in ("%SEARCH_PATHS:;=" "%") do (
    if exist "%%~d" (
        for /d %%j in ("%%~d\jdk*") do (
            if exist "%%~j\bin\java.exe" (
                echo [FOUND] %%~j
                "%%~j\bin\java" -version 2>&1 | findstr /i "version"
            )
        )
    )
)
echo ═══════════════════════════════════════════
```

### 各版本 JDK 工具差异对照表

| 工具/特性 | JDK 8 | JDK 11 | JDK 15 | JDK 17 | JDK 21 | JDK 25 |
|-----------|--------|--------|--------|--------|--------|--------|
| jmap -heap | ✅ | ❌ (移除) | ❌ | ❌ | ❌ | ❌ |
| jmap -dump | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| jcmd GC.heap_dump | ✅ | ✅（推荐） | ✅（推荐） | ✅（推荐） | ✅（推荐） | ✅（推荐） |
| jcmd GC.heap_info | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| jcmd VM.native_memory | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| jcmd Thread.dump_to_file | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| jcmd VM.classloader_stats | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| jhat | ✅ | ❌ (移除) | ❌ | ❌ | ❌ | ❌ |
| jhsdb | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| jfr (内置) | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| GC 日志格式 | `-XX:+PrintGCDetails` | `-Xlog:gc*` | `-Xlog:gc*` | `-Xlog:gc*` | `-Xlog:gc*` | `-Xlog:gc*` |
| PermGen | ✅ | ❌ (Metaspace) | ❌ | ❌ | ❌ | ❌ |
| ZGC | ❌ | ✅ (实验) | ✅ | ✅ (产品级) | ✅ (分代) | ✅ (分代) |
| Shenandoah GC | ❌ | ✅ (部分发行版) | ✅ | ✅ | ✅ | ✅ |
| Virtual Threads | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |

### 版本适配命令映射

执行诊断命令时，根据目标 JDK 版本自动选择正确的命令：

#### Heap Dump 生成

```batch
:: JDK 8
jmap -dump:format=b,file=dump.hprof <PID>

:: JDK 11+ （推荐 jcmd，无需与目标进程 attach）
jcmd <PID> GC.heap_dump dump.hprof

:: JDK 11+ 使用 jhsdb（目标进程已崩溃时）
jhsdb jmap --binaryheap --pid <PID>
```

#### 堆内存概览

```batch
:: JDK 8（jmap -heap 在 JDK 9+ 已移除）
jmap -heap <PID>

:: JDK 11+（替代方案）
jcmd <PID> GC.heap_info

:: JDK 11+ 使用 jhsdb
jhsdb jmap --heap --pid <PID>
```

#### Thread Dump

```batch
:: 所有版本通用
jstack -l <PID>

:: JDK 11+
jcmd <PID> Thread.print

:: JDK 17+（输出到文件，支持 JSON 格式）
jcmd <PID> Thread.dump_to_file -format=json thread_dump.json
```

#### GC 日志配置

```batch
:: JDK 8
-XX:+PrintGCDetails -XX:+PrintGCDateStamps -XX:+PrintGCTimeStamps
-XX:+PrintHeapAtGC -XX:+PrintTenuringDistribution
-Xloggc:gc.log -XX:+UseGCLogFileRotation -XX:NumberOfGCLogFiles=5 -XX:GCLogFileSize=20M

:: JDK 11/15/17/21/25（统一日志框架）
-Xlog:gc*,gc+heap=debug,gc+phases=debug:file=gc.log:time,uptime,level,tags:filecount=5,filesize=20m

:: JDK 21/25（ZGC 分代模式）
-XX:+UseZGC -XX:+ZGenerational
-Xlog:gc*,gc+phases=debug:file=gc.log:time,uptime,level,tags
```

#### Native Memory Tracking

```batch
:: 所有版本（需启动时添加参数）
:: 启动参数：-XX:NativeMemoryTracking=detail
jcmd <PID> VM.native_memory detail

:: 对比模式
jcmd <PID> VM.native_memory baseline
:: ... 等待一段时间 ...
jcmd <PID> VM.native_memory detail.diff
```

#### JFR（Java Flight Recorder）

```batch
:: JDK 8（需商业许可，Oracle JDK）
-XX:+UnlockCommercialFeatures -XX:+FlightRecorder
jcmd <PID> JFR.start name=recording duration=60s filename=record.jfr

:: JDK 11+（免费开放，推荐）
jcmd <PID> JFR.start name=recording duration=60s filename=record.jfr settings=profile

:: 持续记录（用于事后分析）
jcmd <PID> JFR.start name=continuous maxage=1h maxsize=500m disk=true
jcmd <PID> JFR.dump name=continuous filename=dump.jfr
```

### MAT 与 JDK 版本兼容性

| MAT 版本 | 最低 JDK 要求 | 可分析的 Dump JDK 范围 |
|----------|-------------|---------------------|
| MAT 1.8  | JDK 8       | JDK 5 ~ JDK 11     |
| MAT 1.11 | JDK 11      | JDK 5 ~ JDK 15     |
| MAT 1.13 | JDK 11      | JDK 5 ~ JDK 17     |
| MAT 1.14 | JDK 17      | JDK 5 ~ JDK 21     |
| MAT 1.15+| JDK 17      | JDK 5 ~ JDK 25     |

> 注意：用高版本 JDK 生成的 Dump 文件需要对应版本的 MAT 才能正确解析。如果 MAT 报 "Unknown HPROF version" 错误，请升级 MAT。

### 版本选择决策流程

```
用户请求分析
      │
      ▼
  是否指定了 JDK 版本？ ──Yes──▶ 使用指定版本
      │ No
      ▼
  是否有目标 PID？ ──Yes──▶ 检测目标进程 JDK 版本
      │ No                        │
      ▼                           ▼
  是否有 Dump 文件？        使用相同或更高版本 JDK
      │ Yes
      ▼
  从 Dump 文件信息推断版本
      │
      ▼
  使用 JAVA_HOME 或最高可用版本
```

### 不同 GC 收集器推荐

根据 JDK 版本和应用场景，推荐合适的 GC 收集器：

| 场景 | JDK 8 | JDK 11 | JDK 17 | JDK 21/25 |
|------|--------|--------|--------|-----------|
| 低延迟（<10ms） | CMS | ZGC (实验) | ZGC | ZGC 分代 |
| 大堆（>8GB） | G1 | G1 / ZGC | G1 / ZGC | ZGC 分代 |
| 吞吐优先 | Parallel GC | Parallel GC | G1 | G1 |
| 小堆（<2GB） | Parallel GC | G1 | G1 | G1 |
| 容器环境 | G1 + 手动配置 | G1 (自适应) | G1 (自适应) | G1 / ZGC |

---

## 使用示例

```
#java-memory-analyzer
帮我分析这个 Heap Dump 文件：D:/dumps/app-20250609.hprof，看看有没有内存泄漏

#java-memory-analyzer
分析这个 Thread Dump，看看有没有死锁：D:/logs/thread-dump-20250609.txt

#java-memory-analyzer
分析 GC 日志，给我调优建议：D:/logs/gc.log

#java-memory-analyzer
线上 OOM 了，帮我做完整的根因分析，Dump 文件在 /data/dumps/oom-2025-06-09.hprof

#java-memory-analyzer
帮我对比两次 Dump 的差异，看看哪些对象在增长：
  第一次：D:/dumps/before.hprof
  第二次：D:/dumps/after.hprof

#java-memory-analyzer
PID 12345 疑似内存泄漏，帮我采集信息并分析
```

---

## 执行流程

### 场景一：Heap Dump 分析

#### 第一步：确认输入

从用户消息中提取：
- **Dump 文件路径**（必须）：.hprof 文件路径
- **分析目标**（可选）：内存泄漏 / 大对象 / 特定类 / 全面分析
- **可疑包名**（可选）：重点关注的业务包名前缀

#### 第二步：验证文件

```batch
:: 检查文件是否存在及大小
dir "<DUMP文件路径>"

:: 检查文件头魔数（HPROF 文件以 "JAVA PROFILE" 开头）
powershell -Command "Get-Content '<DUMP文件路径>' -TotalCount 1 -Encoding Byte | Format-Hex | Select-Object -First 1"
```

#### 第三步：MAT 命令行分析

```batch
:: 生成 Leak Suspects 报告（最重要）
"%MAT_HOME%\ParseHeapDump.bat" "<DUMP文件路径>" org.eclipse.mat.api:suspects

:: 生成 Top Components 报告
"%MAT_HOME%\ParseHeapDump.bat" "<DUMP文件路径>" org.eclipse.mat.api:top_components
```

#### 第四步：解读 MAT 报告

解压生成的 ZIP 报告文件，读取 HTML 内容，提取以下关键信息：

**Leak Suspects（泄漏嫌疑）**：
- 嫌疑对象的类名和 Retained Heap 大小
- 引用链路（从 GC Root 到目标对象）
- 泄漏占总堆的百分比

**Dominator Tree（支配树）**：
- Top 20 支配者对象及其 Retained Heap
- 按包名/类名聚合分析

**Top Components（大对象）**：
- 内存消耗 Top 组件
- 组件内部对象组成

#### 第五步：补充 OQL 查询（如需要）

对可疑对象做进一步精确查询：

```sql
-- 查找大于 1MB 的 byte[] 对象
SELECT * FROM byte[] s WHERE s.@retainedHeapSize > 1048576

-- 查找所有 HashMap 中 entry 数量大于 10000 的
SELECT m, m.size FROM java.util.HashMap m WHERE m.size > 10000

-- 查找指定类的所有实例
SELECT * FROM com.example.service.OrderCache

-- 查找所有到 GC Root 的路径
SELECT * FROM OBJECTS (SELECT referenceChain FROM java.lang.ref.Finalizer)

-- 查找重复 String
SELECT toString(s), count(s) FROM java.lang.String s GROUP BY toString(s) HAVING count(s) > 100
```

#### 第六步：输出诊断报告

```
═══════════════════════════════════════════════════════════════
📊 Java Heap Dump 分析报告
═══════════════════════════════════════════════════════════════
📁 文件：<文件名>
📏 大小：<文件大小>
🕐 分析时间：<时间>
🔧 工具：Eclipse MAT (ParseHeapDump)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔴 问题总结
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
严重程度：🔴 高危 / 🟡 中等 / 🟢 低
问题类型：内存泄漏 / 大对象 / 集合浪费 / ...
根因定位：<具体类名和引用链>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 详细分析
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【泄漏嫌疑 #1】
├── 对象：com.example.cache.UserSessionCache
├── Retained Heap：1.2 GB（占总堆 60%）
├── 实例数：820,000 个 UserSession 对象
├── GC Root 链：
│   System Class Loader
│   └── com.example.AppContext (static field)
│       └── sessionManager (field)
│           └── ConcurrentHashMap (entries: 820,000)
│               └── UserSession (每个约 1.5KB)
└── 问题分析：Session 对象只增不减，没有过期清理机制

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 修复建议
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. [紧急] 添加 Session TTL 过期清理机制
2. [建议] 使用 WeakReference 或 SoftReference 缓存
3. [优化] 减少 UserSession 对象大小，移除冗余字段

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 JVM 调优参数建议
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
-Xmx4g -Xms4g -XX:+UseG1GC -XX:MaxGCPauseMillis=200
═══════════════════════════════════════════════════════════════
```

---

### 场景二：Thread Dump 分析

#### 第一步：读取 Thread Dump 文件

```batch
type "<ThreadDump文件路径>"
```

#### 第二步：线程状态统计

解析所有线程状态，汇总统计：
- RUNNABLE（运行中）
- BLOCKED（阻塞）
- WAITING（等待）
- TIMED_WAITING（超时等待）

#### 第三步：死锁检测

搜索 `Found one Java-level deadlock` 关键字，或手动分析锁等待链：
- 线程 A 持有锁 X，等待锁 Y
- 线程 B 持有锁 Y，等待锁 X

#### 第四步：热点分析

- 识别大量线程等待同一个锁的情况（锁竞争）
- 识别线程池中 BLOCKED 线程过多的情况（任务阻塞）
- 识别 RUNNABLE 但栈顶为 CPU 密集型操作的线程

#### 第五步：输出报告

```
═══════════════════════════════════════════════════════════════
🧵 Thread Dump 分析报告
═══════════════════════════════════════════════════════════════
📁 文件：<文件名>
🕐 Dump 时间：<时间>
🧮 线程总数：<N> 个

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 线程状态分布
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RUNNABLE:       45 (30%)  ████████████
BLOCKED:        12 (8%)   ████
WAITING:        58 (39%)  ████████████████
TIMED_WAITING:  35 (23%)  █████████

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔴 死锁检测
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[检测结果]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔥 锁竞争热点
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[竞争分析]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 优化建议
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[建议列表]
═══════════════════════════════════════════════════════════════
```

---

### 场景三：GC Log 分析

#### 第一步：读取 GC 日志

支持以下格式：
- JDK 8 格式：`-XX:+PrintGCDetails -XX:+PrintGCDateStamps -Xloggc:gc.log`
- JDK 9+ 统一日志：`-Xlog:gc*:file=gc.log:time,uptime,level,tags`

#### 第二步：解析关键指标

- **GC 次数和频率**：Young GC / Full GC / Mixed GC 次数
- **GC 暂停时间**：平均值 / P50 / P95 / P99 / 最大值
- **内存使用趋势**：各分代使用量随时间变化
- **分配速率**：对象分配速度（MB/s）
- **晋升速率**：对象从 Young 到 Old 的速度

#### 第三步：异常识别

- Full GC 频繁（>1次/分钟）→ 老年代空间不足或内存泄漏
- Full GC 后内存未释放 → 内存泄漏确认
- Young GC 暂停过长（>100ms）→ 年轻代过大
- Allocation Failure → Eden 区过小或分配速率过高
- Metadata GC Threshold → Metaspace 不足

#### 第四步：输出调优建议

根据 GC 日志分析结果，给出具体的 JVM 参数调优建议，包含：
- 堆大小调整（-Xmx / -Xms）
- 分代比例（-XX:NewRatio / -XX:SurvivorRatio）
- GC 收集器选择（G1 / ZGC / Shenandoah）
- GC 目标设置（-XX:MaxGCPauseMillis）

---

### 场景四：在线诊断（需要 PID）

> ⚠️ 执行在线诊断命令前，先检测目标进程的 JDK 版本，参考上方「版本适配命令映射」章节选择正确的命令。

#### 检测目标进程 JDK 版本

```batch
:: 方式 1：通过 jcmd 获取版本信息
jcmd <PID> VM.version

:: 方式 2：通过 jinfo 获取
jinfo -sysprops <PID> 2>&1 | findstr "java.version"

:: 方式 3：查看进程启动命令中的 java 路径
wmic process where "ProcessId=<PID>" get CommandLine
```

#### 采集 Heap Dump

```batch
:: JDK 8（jmap 方式）
jmap -dump:format=b,file=heap_dump.hprof <PID>

:: JDK 11+（推荐 jcmd，更安全、不需要 SA attach）
jcmd <PID> GC.heap_dump heap_dump.hprof

:: JDK 11+（jhsdb 方式，进程已挂起时使用）
jhsdb jmap --binaryheap --dumpfile heap_dump.hprof --pid <PID>

:: 仅 Dump 存活对象（触发一次 Full GC）
jmap -dump:live,format=b,file=heap_dump_live.hprof <PID>
```

#### 采集 Thread Dump

```batch
:: 所有版本通用
jstack -l <PID> > thread_dump.txt

:: JDK 11+
jcmd <PID> Thread.print > thread_dump.txt

:: JDK 17+（支持 JSON 格式输出，含 Virtual Threads）
jcmd <PID> Thread.dump_to_file -format=json thread_dump.json

:: 多次采集（间隔 3 秒，采 3 次，用于对比）
for /L %i in (1,1,3) do (jstack -l <PID> > thread_dump_%i.txt & timeout /t 3)
```

#### 实时 GC 监控

```batch
:: 每秒输出一次 GC 统计（共 10 次）— 所有版本
jstat -gcutil <PID> 1000 10

:: 查看各代容量和使用量
jstat -gc <PID> 1000 5

:: JDK 11+（查看堆信息，替代 jmap -heap）
jcmd <PID> GC.heap_info
```

#### 查看 JVM 参数

```batch
:: 查看所有 JVM 参数
jcmd <PID> VM.flags

:: 查看系统属性
jcmd <PID> VM.system_properties

:: 查看命令行参数
jcmd <PID> VM.command_line

:: JDK 11+（查看类加载器统计，排查 Metaspace 泄漏）
jcmd <PID> VM.classloader_stats
```

#### Native Memory Tracking

```batch
:: 前提：JVM 启动时加上 -XX:NativeMemoryTracking=detail（所有版本）
jcmd <PID> VM.native_memory detail

:: 设置 baseline 并对比
jcmd <PID> VM.native_memory baseline
:: ... 等待一段时间 ...
jcmd <PID> VM.native_memory detail.diff
```

#### JFR 采集（JDK 11+ 免费可用）

```batch
:: 启动 60 秒录制
jcmd <PID> JFR.start name=diagnosis duration=60s filename=diagnosis.jfr settings=profile

:: 持续录制（事后 dump）
jcmd <PID> JFR.start name=continuous maxage=1h maxsize=500m disk=true
jcmd <PID> JFR.dump name=continuous filename=dump.jfr

:: 查看正在进行的录制
jcmd <PID> JFR.check
```

---

### 场景五：Heap Dump 对比分析

#### 第一步：分别生成两次 MAT 索引

```batch
"%MAT_HOME%\ParseHeapDump.bat" "<DUMP1路径>" org.eclipse.mat.api:suspects
"%MAT_HOME%\ParseHeapDump.bat" "<DUMP2路径>" org.eclipse.mat.api:suspects
```

#### 第二步：对比类直方图

提取两次 Dump 中各类的实例数和内存占用，计算增量：

```
═══════════════════════════════════════════════════════════════
📊 Heap Dump 对比分析
═══════════════════════════════════════════════════════════════
时间差：<两次 Dump 间隔>
总堆增长：+512 MB（1.2GB → 1.7GB）

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 增长 Top 10 类
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
| 排名 | 类名                              | 增量实例 | 增量内存  |
|------|-----------------------------------|---------|----------|
| 1    | com.example.dto.OrderSnapshot     | +120000 | +180 MB  |
| 2    | byte[]                            | +85000  | +95 MB   |
| 3    | java.lang.String                  | +90000  | +72 MB   |
| ...  | ...                               | ...     | ...      |
═══════════════════════════════════════════════════════════════
```

---

## 常见 OOM 类型诊断指南

### java.lang.OutOfMemoryError: Java heap space

**原因**：堆内存不足（对象太多或太大）
**诊断步骤**：
1. 用 MAT Leak Suspects 定位大对象
2. 检查是否有缓存无限增长
3. 检查是否有大查询结果集未分页

### java.lang.OutOfMemoryError: Metaspace

**原因**：类元数据区满（动态代理、反射生成类过多）
**诊断步骤**：
1. `jcmd <PID> VM.classloader_stats` 查看类加载器统计
2. 检查 CGLIB / Javassist / Groovy 动态类生成
3. 检查热部署框架是否正确卸载旧类加载器

### java.lang.OutOfMemoryError: unable to create new native thread

**原因**：线程数达到 OS 限制
**诊断步骤**：
1. Thread Dump 分析线程总数和来源
2. 检查线程池是否正确配置了上限
3. 检查 OS 的 `ulimit -u` / `nproc` 限制

### java.lang.OutOfMemoryError: Direct buffer memory

**原因**：堆外直接内存不足（Netty、NIO）
**诊断步骤**：
1. 检查 `-XX:MaxDirectMemorySize` 设置
2. 排查 ByteBuffer.allocateDirect() 未释放
3. 检查 Netty 的 PooledByteBufAllocator 配置

### java.lang.OutOfMemoryError: GC overhead limit exceeded

**原因**：GC 耗时超过 98% 但回收不到 2% 内存
**诊断步骤**：
1. 分析 GC 日志确认 Full GC 后内存占用
2. 用 MAT 分析存活对象，大概率是内存泄漏
3. 检查是否有 Finalizer 队列积压

---

## 高级用法

### MAT OQL 常用查询

```sql
-- 查找最大的 10 个对象
SELECT * FROM INSTANCEOF java.lang.Object ORDER BY @retainedHeapSize DESC LIMIT 10

-- 查找所有线程的线程名和状态
SELECT t.name.toString(), t.threadStatus FROM java.lang.Thread t

-- 查找指定大小以上的 byte[]
SELECT s, s.@length, s.@retainedHeapSize FROM byte[] s WHERE s.@length > 1048576

-- 查找 HashMap 中 Entry 最多的实例
SELECT m, m.size FROM java.util.HashMap m WHERE m.size > 5000 ORDER BY m.size DESC

-- 查找所有 JDBC Connection
SELECT * FROM INSTANCEOF java.sql.Connection

-- 查找所有 ClassLoader 及其加载的类数量
SELECT cl, cl.@objectId FROM INSTANCEOF java.lang.ClassLoader cl

-- 查找所有未关闭的文件流
SELECT * FROM INSTANCEOF java.io.FileInputStream

-- 查找 Spring Bean 定义
SELECT * FROM INSTANCEOF org.springframework.beans.factory.config.BeanDefinition
```

### 批量分析脚本

```batch
@echo off
:: batch-analyze.bat - 批量分析多个 Dump 文件
:: 依赖环境变量 MAT_HOME，使用前请确保已设置
if not defined MAT_HOME (
    echo [ERROR] MAT_HOME is not set. Please set it to your MAT installation directory.
    exit /b 1
)
set DUMP_DIR=%1

for %%f in ("%DUMP_DIR%\*.hprof") do (
    echo Analyzing: %%f
    "%MAT_HOME%\ParseHeapDump.bat" "%%f" org.eclipse.mat.api:suspects org.eclipse.mat.api:top_components
    echo Done: %%f
)
echo All dumps analyzed.
```

### 容器环境采集

```bash
# K8s 环境采集 Heap Dump
kubectl exec <pod-name> -c <container> -- jcmd 1 GC.heap_dump /tmp/dump.hprof
kubectl cp <pod-name>:/tmp/dump.hprof ./dump.hprof -c <container>

# Docker 环境
docker exec <container-id> jcmd 1 GC.heap_dump /tmp/dump.hprof
docker cp <container-id>:/tmp/dump.hprof ./dump.hprof
```

---

## 注意事项

1. **大文件处理**：分析大于 2GB 的 Dump 需要确保 MAT 配置了足够内存（修改 MemoryAnalyzer.ini）
2. **磁盘空间**：MAT 解析时会生成索引文件（约为 Dump 文件大小的 50%~100%），确保磁盘空间充足
3. **分析耗时**：大 Dump 首次解析可能需要 5~30 分钟，后续查询使用索引会很快
4. **隐私安全**：Heap Dump 包含所有内存数据（包括密码、Token 等敏感信息），注意安全处理
5. **版本兼容**：JDK 11+ 的 Dump 需要 MAT 1.11+，JDK 17+ 需要 MAT 1.13+
6. **Windows 路径**：路径中含空格时必须用引号包裹
7. **编码问题**：分析结果中如有中文乱码，检查系统区域设置或加 `-Dfile.encoding=UTF-8`
