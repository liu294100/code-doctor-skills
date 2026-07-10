---
name: jadx-decompile
description: Use JADX to decompile JAR/APK/DEX/AAR files. Especially good for Android apps. Supports CLI batch decompilation and GUI browsing.
inclusion: manual
---

# JADX 反编译 Skill

使用 JADX 反编译 JAR/APK/DEX/AAR 文件，查看 Java 源码。
JADX 特别擅长 Android 相关文件（APK/DEX），同时也支持普通 JAR 包。
使用方式：在聊天中输入 `#jadx-decompile` 并提供文件路径。

---

## 使用示例

```
#jadx-decompile
帮我反编译 D:/apk/some-app.apk 到 D:/output/

#jadx-decompile
用 JADX 查看 some-sdk.jar 中 com.example.SomeClass 的源码

#jadx-decompile
打开 JADX GUI 查看 D:/lib/some.aar

#jadx-decompile
反编译 classes.dex 文件
```

---

## 工具环境

- 统一启动脚本：`D:/dev/tools/decompile.bat`
  - 自动检测 JDK 8 ~ 25，优先高版本
  - 根据 JDK 版本自动选择最佳 JADX 版本和 JVM 参数
- JADX 安装目录：`D:/dev/tools/jadx/`
- JADX CLI：`D:/dev/tools/jadx/bin/jadx.bat`
- JADX GUI：`D:/dev/tools/jadx/bin/jadx-gui.bat`

查看环境信息：
```bash
D:/dev/tools/decompile.bat info
```

---

## JDK 与 JADX 版本兼容性

| JDK 版本 | 推荐 JADX | 说明 |
|:---------|:----------|:-----|
| JDK 8 | 1.4.7 | JADX 最后一个支持 Java 8 的版本 |
| JDK 11 | 1.5.5 | JADX 1.5.x 起最低要求 Java 11 |
| JDK 17 | 1.5.5 | LTS，构建 JADX 源码要求 JDK 17+ |
| JDK 21 | 1.5.5 | LTS，推荐 |
| JDK 22-24 | 1.5.5 | 非 LTS，正常支持 |
| JDK 25 | 1.5.5 | LTS，2025-09-16 GA，推荐 |

**JDK 25** 是最新的 LTS 版本（GA 2025-09-16），新增 Compact Object Headers、Scoped Values、Flexible Constructor Bodies 等特性。JADX 在该版本运行正常。

> JADX 1.4.7 的 `jadx.bat` 中 `-XX:MaxRAMPercentage=70.0` 不兼容 Java 8，`decompile.bat` 会自动处理。

---

## 工具下载

```bash
# 1. 下载统一启动脚本
curl -L -o D:/dev/tools/decompile.bat https://raw.githubusercontent.com/liu294100/code-doctor-check/refs/heads/main/java-doctor-check/decompile.bat

# 2. 下载 JADX（二选一）
# Java 8：
curl -L -o D:/dev/tools/jadx-1.4.7.zip https://github.com/skylot/jadx/releases/download/v1.4.7/jadx-1.4.7.zip
# Java 11+（推荐）：
curl -L -o D:/dev/tools/jadx-1.5.5.zip https://github.com/skylot/jadx/releases/download/v1.5.5/jadx-1.5.5.zip

# 解压
Expand-Archive -Path D:/dev/tools/jadx-1.5.5.zip -DestinationPath D:/dev/tools/jadx -Force

# 3.（可选）CFR 反编译器
curl -L -o D:/dev/tools/cfr.jar https://github.com/leibnitz27/cfr/releases/download/0.152/cfr-0.152.jar
```

多版本共存：
```
D:/dev/tools/
├── decompile.bat       # 统一入口（自动选版本）
├── jadx/               # 1.5.5（JDK 11+）
├── jadx-1.4.7/         # 1.4.7（JDK 8 备用）
└── cfr.jar
```

---

## 支持的文件格式

`.apk` `.dex` `.jar` `.class` `.aar` `.aab` `.xapk` `.apkm` `.smali` `.zip` `.arsc` `.jadx.kts`

---

## JADX CLI 完整参数（v1.5.5）

### 常用参数

| 参数 | 说明 |
|:-----|:-----|
| `-d, --output-dir` | 输出目录 |
| `-ds, --output-dir-src` | 源码输出目录 |
| `-dr, --output-dir-res` | 资源输出目录 |
| `-r, --no-res` | 不反编译资源 |
| `-s, --no-src` | 不反编译源码 |
| `-j, --threads-count` | 线程数（默认 16） |
| `-e, --export-gradle` | 导出为 Gradle 项目 |
| `--show-bad-code` | 显示反编译失败的代码 |
| `--deobf` | 启用反混淆 |
| `--single-class <name>` | 只反编译指定类 |

### 反编译模式

| 参数值 | 说明 |
|:-------|:-----|
| `auto` | 自动选择最佳方式（默认） |
| `restructure` | 还原代码结构（标准 Java） |
| `simple` | 简化指令（线性，含 goto） |
| `fallback` | 原始指令，不做修改 |

用法：`--decompilation-mode restructure`

### 反混淆参数

| 参数 | 说明 |
|:-----|:-----|
| `--deobf` | 启用反混淆 |
| `--deobf-min` | 最短名称长度，更短则重命名（默认 3） |
| `--deobf-max` | 最长名称长度，更长则重命名（默认 64） |
| `--mappings-path` | 映射文件路径（支持 Tiny/Enigma/ProGuard/SRG 等） |

### 其他实用参数

| 参数 | 说明 |
|:-----|:-----|
| `--no-imports` | 不使用 import，写全限定名 |
| `--no-debug-info` | 不解析调试信息 |
| `--no-inline-anonymous` | 不内联匿名类 |
| `--escape-unicode` | 转义非 Latin 字符 |
| `--output-format` | `java`（默认）或 `json` |
| `--comments-level` | 注释级别：error/warn/info/debug/none |
| `--log-level` | 日志级别：quiet/progress/error/warn/info/debug |
| `--config <file>` | 从 JSON 配置文件加载选项 |
| `--save-config <file>` | 保存当前选项为配置文件 |

### 插件参数（-P）

```bash
# 跳过 dex 校验（处理损坏的 APK）
-Pdex-input.verify-checksum=no

# Java 字节码转换模式
-Pjava-convert.mode=both   # dx/d8/both

# Kotlin 元数据利用
-Pkotlin-metadata.class-alias=yes
-Pkotlin-metadata.method-args=yes
```

---

## 执行流程

### 第一步：确认输入参数

从用户消息中提取：
- **输入文件路径**（必须）
- **输出目录**（可选，默认 `D:/tmp/jadx-output`）
- **目标类名**（可选）
- **操作模式**：`cli`（默认）/ `gui` / `single`

### 第二步：CLI 反编译

```bash
# 基本反编译
D:/dev/tools/decompile.bat jadx -d "<输出目录>" "<输入文件>"

# 完整参数（混淆 APK 推荐）
D:/dev/tools/decompile.bat jadx -d "<输出目录>" --deobf --show-bad-code "<输入文件>"

# 只反编译单个类
D:/dev/tools/decompile.bat jadx --single-class "com.example.Target" --single-class-output "Target.java" "<输入文件>"

# 跳过资源加速
D:/dev/tools/decompile.bat jadx -d "<输出目录>" --no-res -j 8 "<输入文件>"

# 导出为 Gradle 项目
D:/dev/tools/decompile.bat jadx -e -d "<输出目录>" "<输入文件>"
```

### 第三步：查看结果

输出目录结构：
```
<输出目录>/
├── sources/           # Java 源码
│   └── com/example/
│       ├── MainActivity.java
│       └── utils/Helper.java
└── resources/         # 资源（APK/AAR 才有）
    ├── AndroidManifest.xml
    ├── res/
    └── assets/
```

```bash
# 查看指定类
type "<输出目录>\sources\com\example\MyClass.java"

# 搜索类文件
dir /s /b "<输出目录>\sources\*.java" | findstr /i "keyword"

# 搜索代码内容
findstr /s /i "someMethod" "<输出目录>\sources\*.java"
```

### 第四步：JADX GUI（可视化）

```bash
D:/dev/tools/decompile.bat jadx-gui "<文件路径>"
```

GUI 功能：代码高亮、跳转声明、查找引用、全文搜索、Smali 调试器、Frida hook 代码生成、反混淆、导出 Gradle 项目。

### 第五步：格式化输出

```
🔍 JADX 反编译结果：com.example.MyClass
═══════════════════════════════════════════
来源：some-app.apk
工具：JADX 1.5.5
输出目录：D:/tmp/jadx-output/
═══════════════════════════════════════════
```

---

## 常见场景

### 反编译 Android APK

```bash
D:/dev/tools/decompile.bat jadx -d D:/tmp/jadx-output/myapp --show-bad-code D:/apk/myapp.apk
type D:\tmp\jadx-output\myapp\resources\AndroidManifest.xml
```

### 反编译混淆 APK

```bash
D:/dev/tools/decompile.bat jadx -d D:/tmp/jadx-output/app --deobf --show-bad-code obfuscated.apk
```

### 反编译 JAR

```bash
D:/dev/tools/decompile.bat jadx -d D:/tmp/jadx-output/lib --no-res some-lib.jar
```

### 只看单个类

```bash
D:/dev/tools/decompile.bat jadx --single-class "com.example.Service" --single-class-output D:/tmp/Service.java app.apk
```

### 处理损坏的 APK

```bash
D:/dev/tools/decompile.bat jadx -d D:/tmp/out --show-bad-code -Pdex-input.verify-checksum=no broken.apk
```

### 保存/复用配置

```bash
# 保存配置
D:/dev/tools/decompile.bat jadx --save-config my-config -d out --deobf --show-bad-code app.apk
# 复用配置
D:/dev/tools/decompile.bat jadx --config my-config app.apk
```

---

## JADX vs CFR 选择指南

| 场景 | 推荐 | 原因 |
|:-----|:-----|:-----|
| Android APK/DEX/AAR/AAB | JADX | 原生支持，含资源解析 |
| 普通 Java JAR | CFR（`#jar-decompile`） | 源码质量更高 |
| 需要 GUI 浏览 | JADX GUI | 可视化 + 调试器 |
| 需要 Frida Hook | JADX GUI | 内置 Frida snippet 生成 |
| 混合使用 | 两者配合 | JADX 看结构，CFR 看细节 |

---

## 注意事项

- 大型 APK 反编译耗时较长，用 `--no-res` 跳过资源可加速
- 混淆代码建议 `--deobf --show-bad-code` 组合
- JADX GUI 需要图形界面环境
- JDK 8 只能用 JADX 1.4.7，不支持 AAB/XAPK 等新格式
- JDK 25（2025-09-16 GA，LTS）推荐作为运行环境
- `decompile.bat` 自动处理版本检测和 JVM 参数适配
