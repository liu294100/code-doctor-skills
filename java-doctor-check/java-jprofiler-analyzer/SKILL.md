---
name: java-jprofiler-analyzer
description: 基于 JProfiler 的 Java 性能与内存深度分析 Skill，支持 Heap Snapshot（.jps）、CPU Snapshot、Thread Dump、Allocation Recording 等离线分析，结合 JProfiler 命令行工具链实现自动化诊断，覆盖内存泄漏、CPU 热点、线程瓶颈、数据库慢查询、锁竞争等全方位性能问题。
inclusion: manual
---

# Java JProfiler Analyzer Skill — JProfiler 性能深度分析

> 基于 JProfiler 的 Java 全栈性能分析 Skill，支持离线 Snapshot 分析和在线 Agent 采集。覆盖内存泄漏、CPU 热点、线程瓶颈、锁竞争、数据库调用、HTTP 请求分析等全方位性能诊断，输出专业报告和优化建议。

---

## 能力范围

你是一个专业的 Java 性能调优工程师，擅长使用 JProfiler 进行以下分析：

### 1. 内存分析（Memory Profiling）
- **堆内存快照分析**：对象实例统计、大对象定位、Retained Size 计算
- **内存泄漏检测**：引用链追踪、GC Root Path 分析、泄漏趋势预测
- **分配热点追踪**：Allocation Hot Spots、分配调用树、临时对象分析
- **分代分析**：Eden/Survivor/Old 对象分布、晋升路径
- **对比分析**：多次 Snapshot 差异对比、增量追踪
- **堆遍历器（Heap Walker）**：按类/包/引用关系自由探索堆内容
- **记录对象分配**：Allocation Recording，追踪每个对象的分配调用栈

### 2. CPU 分析（CPU Profiling）
- **CPU 热点定位**：Hot Spots 视图，按方法排序 CPU 耗时
- **调用树分析**：Call Tree 正向/反向分析调用链路耗时
- **方法统计**：Invocation Count、Self Time、Total Time
- **采样 vs 插桩**：Sampling（低开销）和 Instrumentation（精确）两种模式
- **过滤器配置**：按包名/类名过滤，聚焦业务代码

### 3. 线程分析（Thread Profiling）
- **线程历史**：Thread History 时间线视图
- **线程状态监控**：Running/Waiting/Blocked/Net I/O 状态分布
- **死锁检测**：Monitor & Lock 分析
- **线程转储对比**：多次 Thread Dump 趋势分析
- **Monitor 热点**：高争用锁定位、等待时间统计

### 4. 探针分析（Probes）
- **JDBC 探针**：SQL 执行时间、慢查询、连接池使用率
- **JPA/Hibernate 探针**：N+1 问题、懒加载分析
- **HTTP 探针**：请求耗时、接口性能排名
- **JMS 探针**：消息生产/消费延迟
- **文件 I/O 探针**：文件读写热点
- **Socket 探针**：网络连接状态、数据传输量

### 5. 高级场景
- **Trigger 自动录制**：基于阈值自动触发 Snapshot（CPU > 80%、内存 > 90%）
- **离线分析**：无 GUI 环境命令行分析 Snapshot 文件
- **对比基线**：性能回归对比（版本 A vs 版本 B）
- **MBean 监控**：自定义 JMX MBean 指标实时监控
- **容器环境**：Docker/K8s 中 Agent 集成和远程连接

---

## 工具环境

### 核心工具

| 工具 | 说明 | 用途 |
|------|------|------|
| JProfiler GUI | `%JPROFILER_HOME%\bin\jprofiler.exe` | 可视化分析 Snapshot、实时连接 |
| jpcontroller | `%JPROFILER_HOME%\bin\jpcontroller.exe` | 命令行控制 Agent（触发 Snapshot、开始/停止录制） |
| jpexport | `%JPROFILER_HOME%\bin\jpexport.exe` | 命令行导出 Snapshot 数据为 HTML/CSV/XML |
| jpcompare | `%JPROFILER_HOME%\bin\jpcompare.exe` | 命令行对比两个 Snapshot |
| Agent Library | `%JPROFILER_HOME%\bin\<platform>\jprofilerti.dll` | JVM Agent（附加到目标进程） |

### JPROFILER_HOME 配置

按以下优先级检测 JProfiler 安装路径：

1. **环境变量 `JPROFILER_HOME`**（推荐）
2. **常见安装路径自动探测**：

```batch
:: Windows 常见路径
C:\Program Files\jprofiler<VERSION>
C:\Program Files\jprofiler14
D:\tools\jprofiler
D:\dev\tools\jprofiler
E:\program files\jprofiler

:: Linux
/opt/jprofiler<VERSION>
/usr/local/jprofiler<VERSION>
~/jprofiler<VERSION>

:: macOS
/Applications/JProfiler.app/Contents/Resources/app
```

3. **PATH 中查找**：尝试 `where jpcontroller` / `which jpcontroller`
4. **找不到时提示用户**

### 环境检测脚本

```batch
@echo off
:: detect-jprofiler.bat - 检测 JProfiler 安装
echo ═══════════════════════════════════════════
echo   JProfiler 环境检测
echo ═══════════════════════════════════════════

if defined JPROFILER_HOME (
    if exist "%JPROFILER_HOME%\bin\jpcontroller.exe" (
        echo [OK] JProfiler found: %JPROFILER_HOME%
        "%JPROFILER_HOME%\bin\jpcontroller" --version 2>nul
    ) else (
        echo [ERROR] JPROFILER_HOME is set but jpcontroller not found
    )
) else (
    for %%v in (14 13 12 11) do (
        for %%p in (
            "C:\Program Files\jprofiler%%v"
            "D:\tools\jprofiler%%v"
            "E:\program files\jprofiler%%v"
        ) do (
            if exist "%%~p\bin\jpcontroller.exe" (
                set JPROFILER_HOME=%%~p
                echo [OK] JProfiler %%v auto-detected: %%~p
                goto :found
            )
        )
    )
    echo [ERROR] JProfiler not found. Please set JPROFILER_HOME.
    echo Download: https://www.ej-technologies.com/products/jprofiler/overview.html
)
:found
echo ═══════════════════════════════════════════
```

### JProfiler 安装指引（如未安装）

```
下载地址：https://www.ej-technologies.com/products/jprofiler/overview.html
1. 下载对应平台的安装包（Windows/Linux/macOS）
2. 安装或解压到任意目录
3. 设置环境变量：set JPROFILER_HOME=<安装路径>
4. 激活 License（试用版 10 天免费）

命令行工具无需 GUI License 即可使用 jpexport/jpcompare 分析已有 Snapshot。
```

---

## 多 JDK 版本支持

### JProfiler Agent 版本兼容性

| JProfiler 版本 | 支持的 JDK 版本 | 备注 |
|---------------|----------------|------|
| JProfiler 11  | JDK 5 ~ JDK 15 | 停止更新 |
| JProfiler 12  | JDK 5 ~ JDK 17 | |
| JProfiler 13  | JDK 8 ~ JDK 21 | 支持 Virtual Threads |
| JProfiler 14  | JDK 8 ~ JDK 25 | 最新版，推荐 |

### Agent 附加参数（按 JDK 版本）

```batch
:: JDK 8
-agentpath:"%JPROFILER_HOME%\bin\windows-x64\jprofilerti.dll"=port=8849,nowait

:: JDK 9+（需要额外 module 参数）
-agentpath:"%JPROFILER_HOME%\bin\windows-x64\jprofilerti.dll"=port=8849,nowait
--add-opens java.base/java.lang=ALL-UNNAMED
--add-opens java.base/java.lang.reflect=ALL-UNNAMED
--add-opens java.base/java.util=ALL-UNNAMED

:: JDK 17+（强封装，需要更多 opens）
-agentpath:"%JPROFILER_HOME%\bin\windows-x64\jprofilerti.dll"=port=8849,nowait
--add-opens java.base/java.lang=ALL-UNNAMED
--add-opens java.base/java.lang.reflect=ALL-UNNAMED
--add-opens java.base/java.util=ALL-UNNAMED
--add-opens java.base/jdk.internal.misc=ALL-UNNAMED
--add-opens java.base/sun.nio.ch=ALL-UNNAMED

:: JDK 21+（Virtual Threads 支持）
-agentpath:"%JPROFILER_HOME%\bin\windows-x64\jprofilerti.dll"=port=8849,nowait
--add-opens java.base/java.lang=ALL-UNNAMED
--add-opens java.base/java.lang.reflect=ALL-UNNAMED
--add-opens java.base/java.util=ALL-UNNAMED
--add-opens java.base/java.lang.invoke=ALL-UNNAMED
```

### Linux Agent 路径

```bash
# Linux x64
-agentpath:$JPROFILER_HOME/bin/linux-x64/libjprofilerti.so=port=8849,nowait

# Linux aarch64
-agentpath:$JPROFILER_HOME/bin/linux-aarch64/libjprofilerti.so=port=8849,nowait
```

---

## 使用示例

```
#java-jprofiler-analyzer
帮我分析这个 JProfiler Snapshot：D:/snapshots/app-cpu-20250609.jps，看看 CPU 热点在哪

#java-jprofiler-analyzer
分析内存快照，定位泄漏：D:/snapshots/heap-snapshot.jps

#java-jprofiler-analyzer
帮我对比两次 Snapshot，看性能是否退化：
  基线：D:/snapshots/v1.2.0.jps
  当前：D:/snapshots/v1.3.0.jps

#java-jprofiler-analyzer
PID 8080 的服务响应慢，帮我 attach agent 采集 CPU 和 JDBC 数据

#java-jprofiler-analyzer
导出 Snapshot 的 Hot Spots 为 HTML 报告：D:/snapshots/production.jps

#java-jprofiler-analyzer
分析这个 Snapshot 里的 JDBC 探针数据，找出慢 SQL
```

---

## 执行流程

### 场景一：Snapshot 离线分析

#### 第一步：确认输入

从用户消息中提取：
- **Snapshot 文件路径**（必须）：.jps 文件路径
- **分析类型**（可选）：CPU / Memory / Threads / Probes / 全面分析
- **关注范围**（可选）：特定包名、类名、方法名

#### 第二步：验证文件和环境

```batch
:: 检查 Snapshot 文件
dir "<Snapshot路径>"

:: 检查 JProfiler 工具可用性
"%JPROFILER_HOME%\bin\jpexport.exe" --help 2>nul
if errorlevel 1 echo [ERROR] jpexport not available
```

#### 第三步：使用 jpexport 导出分析数据

```batch
:: 导出 CPU Hot Spots（HTML 格式）
"%JPROFILER_HOME%\bin\jpexport.exe" "<Snapshot路径>" "HotSpots" -format=html -file=hotspots.html

:: 导出 CPU Call Tree
"%JPROFILER_HOME%\bin\jpexport.exe" "<Snapshot路径>" "CallTree" -format=html -file=calltree.html

:: 导出内存分配热点
"%JPROFILER_HOME%\bin\jpexport.exe" "<Snapshot路径>" "AllocationHotSpots" -format=html -file=alloc_hotspots.html

:: 导出堆内存类统计
"%JPROFILER_HOME%\bin\jpexport.exe" "<Snapshot路径>" "HeapWalkerClasses" -format=csv -file=heap_classes.csv

:: 导出线程历史
"%JPROFILER_HOME%\bin\jpexport.exe" "<Snapshot路径>" "ThreadHistory" -format=html -file=threads.html

:: 导出 JDBC 探针（慢 SQL）
"%JPROFILER_HOME%\bin\jpexport.exe" "<Snapshot路径>" "JDBCProbe" -format=html -file=jdbc.html

:: 导出 HTTP 探针
"%JPROFILER_HOME%\bin\jpexport.exe" "<Snapshot路径>" "HTTPProbe" -format=html -file=http.html

:: 导出所有视图
"%JPROFILER_HOME%\bin\jpexport.exe" "<Snapshot路径>" -allViews -format=html -file=full_report.html
```

#### 第四步：解读导出数据

读取导出的 HTML/CSV 文件，提取关键信息：

**CPU Hot Spots**：
- Top 20 耗时方法及其 Self Time / Total Time
- 调用次数（Invocation Count）
- 百分比占比

**Memory**：
- 各类实例数和 Shallow/Retained Size
- 分配热点方法和分配量
- GC Root 引用链

**Threads**：
- 线程状态时间线
- Blocked 时间占比最高的线程
- Monitor 等待统计

**Probes**：
- 慢 SQL Top 10（执行时间、调用次数）
- HTTP 接口耗时排名
- 文件 I/O 热点

#### 第五步：输出诊断报告

```
═══════════════════════════════════════════════════════════════
🔬 JProfiler Snapshot 分析报告
═══════════════════════════════════════════════════════════════
📁 文件：<文件名>
📏 大小：<文件大小>
🕐 录制时长：<录制持续时间>
🔧 工具：JProfiler (jpexport)
📊 分析类型：CPU / Memory / Threads / Probes

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔴 问题总结
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
严重程度：🔴 高危 / 🟡 中等 / 🟢 低
问题类型：CPU 热点 / 内存泄漏 / 线程阻塞 / 慢 SQL / ...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔥 CPU Hot Spots Top 10
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
| 排名 | 方法 | Self Time | Total Time | 调用次数 |
|------|------|-----------|------------|---------|
| 1 | com.example.service.OrderService.calculate() | 2.3s | 5.1s | 12000 |
| 2 | ... | ... | ... | ... |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 内存分配 Top 10
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
| 排名 | 类名 | 实例数 | Shallow Size | Retained Size |
|------|------|--------|-------------|--------------|
| 1 | byte[] | 1,200,000 | 890 MB | 890 MB |
| 2 | ... | ... | ... | ... |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🐢 慢 SQL Top 5（JDBC 探针）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
| 排名 | SQL | 平均耗时 | 调用次数 | 总耗时 |
|------|-----|---------|---------|--------|
| 1 | SELECT * FROM orders WHERE ... | 850ms | 320 | 272s |
| 2 | ... | ... | ... | ... |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 优化建议
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. [CPU] OrderService.calculate() 自循环调用过深，建议引入缓存
2. [Memory] byte[] 分配过于频繁，考虑对象池复用
3. [SQL] orders 表全表扫描，建议添加索引 idx_status_create_time
4. [Thread] pool-3-thread 线程池饱和，建议增大核心线程数
═══════════════════════════════════════════════════════════════
```

---

### 场景二：Snapshot 对比分析

#### 第一步：使用 jpcompare 对比

```batch
:: 对比两个 Snapshot（导出差异报告）
"%JPROFILER_HOME%\bin\jpcompare.exe" "<Snapshot1路径>" "<Snapshot2路径>" -format=html -file=comparison.html

:: 对比特定视图
"%JPROFILER_HOME%\bin\jpcompare.exe" "<Snapshot1路径>" "<Snapshot2路径>" -view=HotSpots -format=csv -file=hotspots_diff.csv
"%JPROFILER_HOME%\bin\jpcompare.exe" "<Snapshot1路径>" "<Snapshot2路径>" -view=HeapWalkerClasses -format=csv -file=heap_diff.csv
```

#### 第二步：解读对比数据

```
═══════════════════════════════════════════════════════════════
📊 JProfiler Snapshot 对比报告
═══════════════════════════════════════════════════════════════
基线：<Snapshot1> (v1.2.0)
当前：<Snapshot2> (v1.3.0)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 CPU 耗时变化 Top 10
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
| 方法 | 基线耗时 | 当前耗时 | 变化 |
|------|---------|---------|------|
| com.example.OrderService.query() | 120ms | 450ms | +275% 🔴 |
| ... | ... | ... | ... |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 内存增长 Top 10
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
| 类名 | 基线实例数 | 当前实例数 | 增量 |
|------|----------|----------|------|
| ... | ... | ... | ... |
═══════════════════════════════════════════════════════════════
```

---

### 场景三：在线 Agent 采集

#### 第一步：检测目标进程

```batch
:: 列出 Java 进程
jps -lv

:: 确认目标进程 JDK 版本
jcmd <PID> VM.version
```

#### 第二步：附加 Agent（两种方式）

**方式 A：启动时附加（推荐，无遗漏）**

```batch
:: 添加到 JVM 启动参数
java -agentpath:"%JPROFILER_HOME%\bin\windows-x64\jprofilerti.dll"=port=8849,nowait -jar app.jar
```

**方式 B：运行时 Attach（无需重启）**

```batch
:: 使用 jpcontroller attach 到运行中进程
"%JPROFILER_HOME%\bin\jpcontroller.exe" --pid=<PID> --start
```

#### 第三步：使用 jpcontroller 控制录制

```batch
:: 连接到 Agent
set JP_CTRL="%JPROFILER_HOME%\bin\jpcontroller.exe" localhost:<PORT>

:: 开始 CPU 录制
%JP_CTRL% "startCPURecording"

:: 开始内存分配录制
%JP_CTRL% "startAllocRecording"

:: 开始探针录制（JDBC、HTTP 等）
%JP_CTRL% "startProbeRecording" "JDBC"
%JP_CTRL% "startProbeRecording" "HTTP"

:: 等待一段时间采集数据...
timeout /t 60

:: 停止录制
%JP_CTRL% "stopCPURecording"
%JP_CTRL% "stopAllocRecording"
%JP_CTRL% "stopProbeRecording" "JDBC"

:: 保存 Snapshot
%JP_CTRL% "saveSnapshot" "D:\snapshots\diagnosis_%date:~0,10%.jps"

:: 触发堆内存 Snapshot
%JP_CTRL% "triggerHeapDump"

:: 触发线程 Dump
%JP_CTRL% "triggerThreadDump"
```

#### 第四步：断开并分析

```batch
:: 断开连接（不影响目标进程）
%JP_CTRL% "disconnect"

:: 导出分析（参考场景一）
"%JPROFILER_HOME%\bin\jpexport.exe" "D:\snapshots\diagnosis_2025-06-09.jps" -allViews -format=html -file=report.html
```

---

### 场景四：Trigger 自动录制

配置 JProfiler Trigger 在异常时自动保存 Snapshot，无需人工介入：

#### 常用 Trigger 配置

```xml
<!-- 在 JProfiler session 配置中添加 -->
<triggers>
  <!-- CPU 使用超过 80% 时自动录制 -->
  <trigger name="High CPU" type="cpuLoad" threshold="80" duration="10s">
    <action type="startCPURecording"/>
    <action type="saveSnapshotAfter" delay="30s"/>
  </trigger>

  <!-- 堆内存使用超过 90% 时触发 Heap Dump -->
  <trigger name="High Memory" type="heapUsage" threshold="90">
    <action type="triggerHeapDump"/>
    <action type="saveSnapshot"/>
  </trigger>

  <!-- 检测到死锁时保存 Thread Dump -->
  <trigger name="Deadlock" type="deadlock">
    <action type="triggerThreadDump"/>
    <action type="saveSnapshot"/>
  </trigger>

  <!-- Full GC 后内存未释放时触发 -->
  <trigger name="Memory Leak" type="gcActivity" oldGenAfterGC="85">
    <action type="startAllocRecording"/>
    <action type="triggerHeapDump"/>
    <action type="saveSnapshotAfter" delay="60s"/>
  </trigger>
</triggers>
```

#### 命令行设置 Trigger

```batch
:: 使用 config 文件启动（包含 Trigger 定义）
java -agentpath:"%JPROFILER_HOME%\bin\windows-x64\jprofilerti.dll"=port=8849,nowait,config=%JPROFILER_HOME%\config\my-triggers.xml -jar app.jar
```

---

### 场景五：容器环境集成

#### Docker 环境

```dockerfile
# Dockerfile 中添加 JProfiler Agent
FROM openjdk:17-slim

# 复制 JProfiler Agent
COPY jprofiler-agent/ /opt/jprofiler/

# 环境变量
ENV JPROFILER_HOME=/opt/jprofiler
ENV JPROFILER_AGENT="-agentpath:/opt/jprofiler/bin/linux-x64/libjprofilerti.so=port=8849,nowait"

# 启动时附加 Agent（通过环境变量控制是否开启）
ENTRYPOINT ["sh", "-c", "java ${JPROFILER_AGENT:-} -jar /app/app.jar"]
```

```bash
# 启动容器时暴露 JProfiler 端口
docker run -p 8849:8849 -e JPROFILER_AGENT="-agentpath:/opt/jprofiler/bin/linux-x64/libjprofilerti.so=port=8849,nowait" myapp

# 从容器中拷贝 Snapshot
docker cp <container>:/tmp/snapshot.jps ./snapshot.jps
```

#### Kubernetes 环境

```yaml
# Pod spec 中添加 JProfiler sidecar 或 initContainer
spec:
  containers:
  - name: app
    image: myapp:latest
    env:
    - name: JAVA_TOOL_OPTIONS
      value: "-agentpath:/opt/jprofiler/bin/linux-x64/libjprofilerti.so=port=8849,nowait"
    ports:
    - containerPort: 8849
      name: jprofiler
    volumeMounts:
    - name: jprofiler-agent
      mountPath: /opt/jprofiler
  initContainers:
  - name: jprofiler-init
    image: jprofiler-agent:14
    command: ["cp", "-r", "/jprofiler/.", "/opt/jprofiler/"]
    volumeMounts:
    - name: jprofiler-agent
      mountPath: /opt/jprofiler
  volumes:
  - name: jprofiler-agent
    emptyDir: {}
```

```bash
# 端口转发到本地
kubectl port-forward pod/<pod-name> 8849:8849

# 本地 JProfiler GUI 连接 localhost:8849
```

---

## JProfiler vs MAT 选择指南

| 场景 | 推荐工具 | 原因 |
|------|---------|------|
| 纯 Heap Dump (.hprof) 分析 | MAT | MAT 的 Leak Suspects 和 OQL 更强大 |
| CPU 性能热点定位 | JProfiler | 调用树和热点视图更直观 |
| 内存泄漏 + 分配追踪 | JProfiler | 能追踪每个对象的分配调用栈 |
| 线程问题诊断 | JProfiler | Thread History 时间线可视化 |
| 数据库慢查询 | JProfiler | JDBC 探针能关联 SQL 和调用栈 |
| 生产环境事后分析 | MAT | 只需 .hprof 文件，不需要 Agent |
| 性能回归测试 | JProfiler | jpcompare 支持自动化对比 |
| 开发阶段调优 | JProfiler | 实时连接，边改边测 |

> 建议同时安装 MAT 和 JProfiler，MAT 用于生产 Dump 分析，JProfiler 用于开发/测试阶段全栈 Profiling。

---

## 常见问题排查

### Agent 连接失败

```batch
:: 检查 Agent 是否加载成功（看启动日志）
:: 正常应有：JProfiler> Protocol version XX
:: 检查端口是否监听
netstat -ano | findstr 8849

:: 防火墙放行
netsh advfirewall firewall add rule name="JProfiler" dir=in action=allow protocol=tcp localport=8849
```

### Snapshot 文件过大

```batch
:: 录制时设置过滤器，减少无关数据
:: 启动参数添加过滤包名
-agentpath:...=port=8849,nowait,config=jprofiler_config.xml

:: jprofiler_config.xml 中配置过滤器
:: <filters><include>com.example.*</include><exclude>org.springframework.*</exclude></filters>
```

### 高版本 JDK 附加问题

```batch
:: JDK 16+ 强封装，Attach 可能失败，需要：
:: 方式 1：启动时加参数
-XX:+AllowRedefinitionToAddDeleteMethods

:: 方式 2：使用 jcmd 确认 Attach 可用
jcmd <PID> VM.flags | findstr "DisableAttachMechanism"
:: 确保没有 -XX:+DisableAttachMechanism
```

---

## 注意事项

1. **性能开销**：Agent Instrumentation 模式开销约 5~15%，Sampling 模式约 1~3%，生产环境推荐 Sampling
2. **License**：JProfiler 为商业软件，命令行导出工具（jpexport/jpcompare）需要有效 License
3. **磁盘空间**：Snapshot 文件可能很大（几百 MB 到几 GB），确保磁盘充足
4. **安全性**：Snapshot 包含运行时数据（包括字符串常量、请求参数等），注意隐私
5. **版本匹配**：分析 Snapshot 的 JProfiler 版本需要 >= 录制时的版本
6. **Attach 限制**：部分容器或安全策略禁止动态 Attach，此时只能在启动时添加 Agent
7. **Virtual Threads（JDK 21+）**：JProfiler 13+ 支持虚拟线程分析，低版本无法正确展示
