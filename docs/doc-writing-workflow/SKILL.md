---
name: doc-writer
description: 专业技术文档写作与 Mermaid 图表生成，支持导出 HTML/PDF/DOCX 格式
inclusion: manual
---

# 高效文档写作 Steering

## 核心原则

当需要生成 Markdown 文档时，遵循以下工作流，确保高效、一次成功。

## 文件写入策略（关键）

由于 `fs_write` 工具对大文本存在限制，PowerShell here-string 对特殊字符（反引号、端口号等）有转义问题，
**必须使用 Python 脚本作为文件写入引擎**：

1. 先用 `fs_write` 创建一个临时 Python 脚本（如 `_write_doc.py`）
2. 在脚本中用 triple-quoted string 包含完整文档内容
3. 用 `pathlib.Path.write_text()` 写入目标 .md 文件
4. 执行脚本后删除临时脚本

### 模板

```python
#!/usr/bin/env python3
"""临时文档生成脚本 - 执行后自动删除"""
from pathlib import Path

content = """
# 文档标题

正文内容...
"""

target = Path(r"目标路径.md")
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(content.strip(), encoding="utf-8")
print(f"Done: {target} ({target.stat().st_size} bytes)")

# 自删除
Path(__file__).unlink()
```

### 为什么这样做

- Python triple-quote 对 Markdown 中的反引号、特殊字符零冲突
- 一次执行写入完整文件，不需要分段 append
- 脚本自删除，不留垃圾文件
- 支持任意大小的文档

## 文档写作流程

### Phase 1: 信息收集（快速）

- 如果涉及外部资料（URL），先用 web_search 获取摘要信息
- 如果涉及代码库，用 grep_search / readCode 快速定位关键代码
- 不要过度收集，够用即可

### Phase 2: 大纲确认（可选）

- 对于复杂文档（预计 > 200 行），先列出大纲让用户确认
- 简单文档直接写

### Phase 3: 一次性生成

- 用上述 Python 脚本方式一次性写入完整文档
- 不要分段写入（避免多次 shell 调用的开销和出错风险）

### Phase 4: 验证

- 用 `read_file` 检查文件头尾确认完整性
- 报告文件行数和大小

## 文档质量标准

### 结构

- 一个 `#` 一级标题
- 标题层级严格递增
- 开头有 `>` 引用块做摘要
- 结尾有参考资料链接

### 内容

- 中英文之间加空格
- 代码块指定语言
- 表格对齐
- 复杂流程用 ASCII 图或 Mermaid
- 每个概念配示例

### 项目特定

- 文档放在 `doc/biz/doc/` 目录
- API 文档放在 `doc/biz/doc/api/` 目录
- 文件名用英文小写 + 下划线
- 内部文档互相引用用相对路径

## 文档类型模板

### 技术方案文档

```
# [方案名称]
> 一句话描述

---
## 1. 背景与目标
## 2. 现状分析
## 3. 方案设计（含架构图）
## 4. 核心实现（含代码示例）
## 5. 部署方案
## 6. 使用示例
## 7. 注意事项与限制
## 8. 后续演进
## 参考资料
```

### API 文档

```
# [API 名称]
> 接口用途一句话

---
## 接口信息
## 请求参数
## 响应结构
## 调用示例
## 错误码
## 注意事项
```

### 部署配置文档

```
# [服务名] 部署配置
> 环境和配置说明

---
## 1. 环境要求
## 2. 配置参数
## 3. 部署步骤
## 4. 健康检查
## 5. 常见问题
## 参考链接
```
