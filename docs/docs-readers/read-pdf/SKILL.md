---
name: read-pdf
description: Read PDF files and extract text content, tables, and metadata using Python pdfplumber.
---

# PDF 读取 Skill

读取 PDF 文件内容，提取文本、表格等信息。
使用方式：在聊天中输入 `#read-pdf` 并提供 PDF 文件路径。

---

## 使用示例

```
#read-pdf
帮我读取 doc/design/524Mindmap.pdf 的内容

#read-pdf
提取 D:/docs/report.pdf 第3-5页的内容

#read-pdf
读取 D:/docs/data.pdf 中的表格数据
```

---

## 依赖环境

- Python 3.x
- pdfplumber（已安装）

如未安装：
```bash
pip install pdfplumber
```

---

## 执行流程

### 第一步：确认参数

- **文件路径**（必须）
- **页码范围**（可选）：如 "第3页"、"第3-5页"、"全部"（默认全部）
- **提取模式**（可选）：
  - `text` - 提取纯文本（默认）
  - `table` - 提取表格
  - `all` - 文本+表格

### 第二步：读取 PDF

使用 Python 脚本读取，根据用户需求选择合适的脚本：

#### 提取全部文本

```bash
python -c "
import pdfplumber
pdf = pdfplumber.open(r'<PDF路径>')
for i, page in enumerate(pdf.pages):
    text = page.extract_text()
    if text:
        print(f'--- 第 {i+1} 页 ---')
        print(text)
pdf.close()
"
```

#### 提取指定页码

```bash
python -c "
import pdfplumber
pdf = pdfplumber.open(r'<PDF路径>')
pages = pdf.pages[<起始页-1>:<结束页>]  # 0-indexed
for i, page in enumerate(pages, start=<起始页>):
    text = page.extract_text()
    if text:
        print(f'--- 第 {i} 页 ---')
        print(text)
pdf.close()
"
```

#### 提取表格

```bash
python -c "
import pdfplumber, json
pdf = pdfplumber.open(r'<PDF路径>')
for i, page in enumerate(pdf.pages):
    tables = page.extract_tables()
    for j, table in enumerate(tables):
        print(f'--- 第 {i+1} 页 表格 {j+1} ---')
        for row in table:
            print(' | '.join([str(cell) if cell else '' for cell in row]))
        print()
pdf.close()
"
```

#### 获取 PDF 基本信息

```bash
python -c "
import pdfplumber
pdf = pdfplumber.open(r'<PDF路径>')
print(f'页数: {len(pdf.pages)}')
if pdf.metadata:
    for k, v in pdf.metadata.items():
        print(f'{k}: {v}')
pdf.close()
"
```

### 第三步：格式化输出

```
📄 PDF 内容：filename.pdf
═══════════════════════════════════════════
页数：X 页
═══════════════════════════════════════════

--- 第 1 页 ---
（文本内容）

--- 第 2 页 ---
（文本内容）
```

---

## 注意事项

- 扫描版 PDF（图片型）无法直接提取文本，需要 OCR 工具
- 复杂排版的 PDF 提取的文本顺序可能不完全准确
- 表格提取对简单表格效果好，复杂合并单元格可能不准确
- 大型 PDF 建议指定页码范围，避免输出过多
