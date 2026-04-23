---
name: read-ppt
description: Read PowerPoint (.pptx) files and extract slide text, notes, tables, and outline structure using Python python-pptx.
---

# PPT 读取 Skill

读取 PowerPoint（.pptx）文件内容，提取幻灯片文本、备注、表格等信息。
使用方式：在聊天中输入 `#read-ppt` 并提供文件路径。

---

## 使用示例

```
#read-ppt
帮我读取 D:/docs/方案汇报.pptx 的内容

#read-ppt
提取 D:/docs/presentation.pptx 第5-10页的内容

#read-ppt
查看 D:/docs/design.pptx 的大纲结构
```

---

## 依赖环境

- Python 3.x
- python-pptx（已安装）

如未安装：
```bash
pip install python-pptx
```

---

## 执行流程

### 第一步：确认参数

- **文件路径**（必须）
- **页码范围**（可选）：如 "第5页"、"第5-10页"、"全部"（默认全部）
- **提取模式**（可选）：
  - `text` - 提取文本（默认）
  - `outline` - 提取大纲结构
  - `notes` - 提取备注
  - `table` - 提取表格
  - `all` - 全部内容

### 第二步：读取 PPT

#### 获取基本信息

```bash
python -c "
from pptx import Presentation
from pptx.util import Inches, Pt
prs = Presentation(r'<PPTX路径>')
print(f'幻灯片数量: {len(prs.slides)}')
print(f'宽度: {prs.slide_width}')
print(f'高度: {prs.slide_height}')
if prs.core_properties.title:
    print(f'标题: {prs.core_properties.title}')
if prs.core_properties.author:
    print(f'作者: {prs.core_properties.author}')
"
```

#### 提取全部文本

```bash
python -c "
from pptx import Presentation
prs = Presentation(r'<PPTX路径>')
for i, slide in enumerate(prs.slides, 1):
    texts = []
    for shape in slide.shapes:
        if shape.has_text_frame:
            for para in shape.text_frame.paragraphs:
                text = para.text.strip()
                if text:
                    texts.append(text)
    if texts:
        print(f'--- 第 {i} 页 ---')
        for t in texts:
            print(t)
        print()
"
```

#### 提取指定页码

```bash
python -c "
from pptx import Presentation
prs = Presentation(r'<PPTX路径>')
start, end = <起始页>, <结束页>  # 1-indexed
for i, slide in enumerate(prs.slides, 1):
    if i < start or i > end:
        continue
    texts = []
    for shape in slide.shapes:
        if shape.has_text_frame:
            for para in shape.text_frame.paragraphs:
                text = para.text.strip()
                if text:
                    texts.append(text)
    if texts:
        print(f'--- 第 {i} 页 ---')
        for t in texts:
            print(t)
        print()
"
```

#### 提取大纲结构（标题+副标题）

```bash
python -c "
from pptx import Presentation
prs = Presentation(r'<PPTX路径>')
for i, slide in enumerate(prs.slides, 1):
    title = ''
    subtitle = ''
    for shape in slide.shapes:
        if shape.shape_type == 13 or (hasattr(shape, 'placeholder_format') and shape.placeholder_format is not None):
            ph_idx = shape.placeholder_format.idx if shape.placeholder_format else -1
            if ph_idx == 0:
                title = shape.text.strip()
            elif ph_idx == 1:
                subtitle = shape.text.strip()
    if title:
        print(f'{i}. {title}')
        if subtitle:
            print(f'   {subtitle}')
"
```

#### 提取备注

```bash
python -c "
from pptx import Presentation
prs = Presentation(r'<PPTX路径>')
for i, slide in enumerate(prs.slides, 1):
    if slide.has_notes_slide:
        notes = slide.notes_slide.notes_text_frame.text.strip()
        if notes:
            print(f'--- 第 {i} 页备注 ---')
            print(notes)
            print()
"
```

#### 提取表格

```bash
python -c "
from pptx import Presentation
prs = Presentation(r'<PPTX路径>')
for i, slide in enumerate(prs.slides, 1):
    for shape in slide.shapes:
        if shape.has_table:
            table = shape.table
            print(f'--- 第 {i} 页 表格 ({len(table.rows)}x{len(table.columns)}) ---')
            for row in table.rows:
                cells = [cell.text.strip() for cell in row.cells]
                print(' | '.join(cells))
            print()
"
```

#### 提取全部内容（文本+表格+备注）

```bash
python -c "
from pptx import Presentation
prs = Presentation(r'<PPTX路径>')
for i, slide in enumerate(prs.slides, 1):
    print(f'=== 第 {i} 页 ===')
    for shape in slide.shapes:
        if shape.has_text_frame:
            for para in shape.text_frame.paragraphs:
                text = para.text.strip()
                if text:
                    print(text)
        if shape.has_table:
            table = shape.table
            print(f'[表格 {len(table.rows)}x{len(table.columns)}]')
            for row in table.rows:
                cells = [cell.text.strip() for cell in row.cells]
                print('| ' + ' | '.join(cells) + ' |')
    if slide.has_notes_slide:
        notes = slide.notes_slide.notes_text_frame.text.strip()
        if notes:
            print(f'[备注] {notes}')
    print()
"
```

### 第三步：格式化输出

```
📊 PPT 内容：filename.pptx
═══════════════════════════════════════════
幻灯片数量：X 页
═══════════════════════════════════════════

=== 第 1 页 ===
标题内容
正文内容

=== 第 2 页 ===
...
```

---

## 注意事项

- 只支持 `.pptx` 格式（Office 2007+），不支持旧版 `.ppt`
- 图片、图表、SmartArt 等非文本内容无法提取
- 动画和过渡效果信息不会被提取
- 嵌入的音视频无法处理
- 大型 PPT 建议指定页码范围
