---
name: read-docx
description: Read Word (.docx) files and extract text, headings outline, and tables using Python python-docx.
---

# DOCX 读取 Skill

读取 Word（.docx）文件内容，提取文本、表格、标题结构等信息。
使用方式：在聊天中输入 `#read-docx` 并提供文件路径。

---

## 使用示例

```
#read-docx
帮我读取 D:/docs/需求文档.docx 的内容

#read-docx
提取 D:/docs/report.docx 中的所有表格

#read-docx
查看 D:/docs/design.docx 的标题大纲结构
```

---

## 依赖环境

- Python 3.x
- python-docx（已安装）

如未安装：
```bash
pip install python-docx
```

---

## 执行流程

### 第一步：确认参数

- **文件路径**（必须）
- **提取模式**（可选）：
  - `text` - 提取全部文本（默认）
  - `table` - 提取表格
  - `outline` - 提取标题大纲
  - `all` - 文本+表格+大纲

### 第二步：读取 DOCX

#### 提取全部文本

```bash
python -c "
from docx import Document
doc = Document(r'<DOCX路径>')
for para in doc.paragraphs:
    if para.text.strip():
        prefix = ''
        if para.style.name.startswith('Heading'):
            level = para.style.name.replace('Heading ', '')
            prefix = '#' * int(level) + ' ' if level.isdigit() else ''
        print(f'{prefix}{para.text}')
"
```

#### 提取标题大纲

```bash
python -c "
from docx import Document
doc = Document(r'<DOCX路径>')
for para in doc.paragraphs:
    if para.style.name.startswith('Heading'):
        level = para.style.name.replace('Heading ', '')
        indent = '  ' * (int(level) - 1) if level.isdigit() else ''
        print(f'{indent}- {para.text}')
"
```

#### 提取表格

```bash
python -c "
from docx import Document
doc = Document(r'<DOCX路径>')
for i, table in enumerate(doc.tables):
    print(f'--- 表格 {i+1} ---')
    for row in table.rows:
        cells = [cell.text.strip() for cell in row.cells]
        print(' | '.join(cells))
    print()
"
```

#### 提取全部内容（文本+表格，按文档顺序）

```bash
python -c "
from docx import Document
from docx.oxml.ns import qn
doc = Document(r'<DOCX路径>')
for element in doc.element.body:
    if element.tag == qn('w:p'):
        text = element.text
        if text and text.strip():
            print(text)
    elif element.tag == qn('w:tbl'):
        from docx.table import Table
        table = Table(element, doc)
        print()
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells]
            print('| ' + ' | '.join(cells) + ' |')
        print()
"
```

#### 获取文档基本信息

```bash
python -c "
from docx import Document
doc = Document(r'<DOCX路径>')
props = doc.core_properties
print(f'标题: {props.title}')
print(f'作者: {props.author}')
print(f'创建时间: {props.created}')
print(f'修改时间: {props.modified}')
print(f'段落数: {len(doc.paragraphs)}')
print(f'表格数: {len(doc.tables)}')
"
```

### 第三步：格式化输出

```
📝 DOCX 内容：filename.docx
═══════════════════════════════════════════
段落数：X | 表格数：X
═══════════════════════════════════════════

（文档内容，标题用 Markdown 格式展示）
```

---

## 注意事项

- 只支持 `.docx` 格式（Office 2007+），不支持旧版 `.doc`
- 图片内容无法提取为文本
- 复杂排版（文本框、艺术字等）可能无法完整提取
- 嵌套表格会被展平显示
