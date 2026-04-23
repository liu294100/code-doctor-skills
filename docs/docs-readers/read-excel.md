---
inclusion: manual
---

# Excel 读取 Skill

读取 Excel（.xlsx/.xls）文件内容，提取工作表数据、结构信息。
使用方式：在聊天中输入 `#read-excel` 并提供文件路径。

---

## 使用示例

```
#read-excel
帮我读取 doc/excel/Fees_20260316.xlsx 的内容

#read-excel
查看 D:/data/report.xlsx 中 Sheet2 的数据

#read-excel
读取 D:/data/data.xls 前 20 行
```

---

## 依赖环境

- Python 3.x
- openpyxl（已安装，读取 .xlsx）
- xlrd（已安装，读取 .xls）
- pandas（已安装，通用读取）

如未安装：
```bash
pip install openpyxl xlrd pandas
```

---

## 执行流程

### 第一步：确认参数

- **文件路径**（必须）
- **工作表名**（可选）：指定 Sheet 名称，默认读取所有 Sheet
- **行数限制**（可选）：如 "前20行"、"全部"（默认全部）
- **输出格式**（可选）：
  - `table` - 表格格式（默认）
  - `csv` - CSV 格式
  - `json` - JSON 格式

### 第二步：读取 Excel

#### 查看工作表列表和基本信息

```bash
python -c "
import openpyxl
wb = openpyxl.load_workbook(r'<XLSX路径>', read_only=True, data_only=True)
print(f'工作表数量: {len(wb.sheetnames)}')
for name in wb.sheetnames:
    ws = wb[name]
    print(f'  [{name}] 行数={ws.max_row} 列数={ws.max_column}')
wb.close()
"
```

#### 使用 pandas 读取（推荐，通用性最好）

```bash
python -c "
import pandas as pd
# .xlsx 文件
df = pd.read_excel(r'<文件路径>', sheet_name='<Sheet名或0>', engine='openpyxl')
# .xls 文件
# df = pd.read_excel(r'<文件路径>', sheet_name='<Sheet名或0>', engine='xlrd')
print(f'行数: {len(df)}, 列数: {len(df.columns)}')
print(f'列名: {list(df.columns)}')
print()
print(df.to_string(index=False))
"
```

#### 读取指定行数

```bash
python -c "
import pandas as pd
df = pd.read_excel(r'<文件路径>', sheet_name=0, engine='openpyxl', nrows=<行数>)
print(df.to_string(index=False))
"
```

#### 读取所有 Sheet

```bash
python -c "
import pandas as pd
sheets = pd.read_excel(r'<文件路径>', sheet_name=None, engine='openpyxl')
for name, df in sheets.items():
    print(f'=== Sheet: {name} ({len(df)} 行 x {len(df.columns)} 列) ===')
    print(df.to_string(index=False))
    print()
"
```

#### 输出为 Markdown 表格

```bash
python -c "
import pandas as pd
df = pd.read_excel(r'<文件路径>', sheet_name=0, engine='openpyxl')
print(df.to_markdown(index=False))
"
```

#### 输出为 CSV

```bash
python -c "
import pandas as pd
df = pd.read_excel(r'<文件路径>', sheet_name=0, engine='openpyxl')
print(df.to_csv(index=False))
"
```

#### 输出为 JSON

```bash
python -c "
import pandas as pd
df = pd.read_excel(r'<文件路径>', sheet_name=0, engine='openpyxl')
print(df.to_json(orient='records', force_ascii=False, indent=2))
"
```

#### 读取旧版 .xls 文件

```bash
python -c "
import pandas as pd
df = pd.read_excel(r'<XLS路径>', sheet_name=0, engine='xlrd')
print(df.to_string(index=False))
"
```

### 第三步：格式化输出

```
📊 Excel 内容：filename.xlsx
═══════════════════════════════════════════
工作表：Sheet1 | 行数：X | 列数：X
═══════════════════════════════════════════

（表格数据，用 Markdown 表格或对齐文本展示）
```

---

## 大文件处理策略

- 超过 100 行：默认只显示前 50 行 + 后 10 行，提示用户指定范围
- 超过 20 列：考虑只显示关键列，或转为纵向展示
- 多 Sheet 文件：先列出所有 Sheet 信息，让用户选择

```bash
# 大文件只读前 N 行
python -c "
import pandas as pd
df = pd.read_excel(r'<文件路径>', nrows=50, engine='openpyxl')
print(f'(仅显示前 50 行，共 {pd.read_excel(r\"<文件路径>\", engine=\"openpyxl\").shape[0]} 行)')
print(df.to_string(index=False))
"
```

---

## 注意事项

- `.xlsx` 使用 openpyxl 引擎，`.xls` 使用 xlrd 引擎
- `data_only=True` 读取公式计算后的值（而非公式本身）
- 合并单元格只在左上角有值，其余为 None
- 日期列可能需要格式化处理
- 非常大的文件（>10MB）建议分页读取
