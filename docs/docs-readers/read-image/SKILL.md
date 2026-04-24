---
name: read-image
description: 读取图片文件并提取文字内容、元数据信息，支持 OCR 文字识别、EXIF 元数据查看、图片基本属性获取，使用 Python Pillow + pytesseract。
---

# 图片读取 Skill

读取图片文件，提取文字（OCR）、元数据（EXIF）、基本属性等信息。
使用方式：在聊天中输入 `#read-image` 并提供图片文件路径。

---

## 使用示例

```
#read-image
帮我识别 doc/screenshot.png 中的文字

#read-image
读取 D:/photos/receipt.jpg 的 EXIF 信息

#read-image
提取 assets/diagram.png 的基本信息和文字内容

#read-image
识别 D:/docs/scan001.tiff 中的中文文字
```

---

## 依赖环境

- Python 3.x
- Pillow（图片处理）
- pytesseract（OCR 文字识别，可选）
- Tesseract-OCR 引擎（pytesseract 的后端，可选）

安装命令：

```bash
# 基础依赖（图片属性 + EXIF）
pip install Pillow

# OCR 文字识别（可选）
pip install pytesseract
```

Tesseract-OCR 引擎安装：

```bash
# Windows — 下载安装包：https://github.com/UB-Mannheim/tesseract/wiki
# 安装后将 tesseract.exe 路径加入 PATH

# macOS
brew install tesseract

# Linux (Ubuntu/Debian)
sudo apt install tesseract-ocr

# 中文语言包（如需识别中文）
# Windows: 安装时勾选 Chinese Simplified
# Linux: sudo apt install tesseract-ocr-chi-sim
```

---

## 执行流程

### 第一步：确认参数

- **文件路径**（必须）：支持 PNG、JPG/JPEG、BMP、TIFF、GIF、WebP
- **提取模式**（可选）：
  - `info` — 图片基本属性（尺寸、格式、色彩模式）
  - `ocr` — OCR 文字识别
  - `exif` — EXIF 元数据
  - `all` — 全部信息（默认）
- **OCR 语言**（可选）：`eng`（默认）、`chi_sim`（简体中文）、`chi_sim+eng`（中英混合）

### 第二步：读取图片

根据用户需求选择合适的脚本：

#### 获取图片基本信息

```bash
python -c "
from PIL import Image
import os
img = Image.open(r'<图片路径>')
path = r'<图片路径>'
print(f'文件: {os.path.basename(path)}')
print(f'大小: {os.path.getsize(path) / 1024:.1f} KB')
print(f'格式: {img.format}')
print(f'尺寸: {img.size[0]} x {img.size[1]} px')
print(f'色彩模式: {img.mode}')
if hasattr(img, 'n_frames'):
    print(f'帧数: {img.n_frames}')
img.close()
"
```

#### OCR 文字识别

```bash
python -c "
from PIL import Image
import pytesseract
img = Image.open(r'<图片路径>')
text = pytesseract.image_to_string(img, lang='<语言代码>')
print(text if text.strip() else '（未识别到文字内容）')
img.close()
"
```

语言代码参考：
- `eng` — 英文
- `chi_sim` — 简体中文
- `chi_tra` — 繁体中文
- `jpn` — 日文
- `kor` — 韩文
- `chi_sim+eng` — 中英混合

#### OCR 预处理（提高识别率）

```bash
python -c "
from PIL import Image, ImageFilter, ImageEnhance
import pytesseract
img = Image.open(r'<图片路径>')
# 转灰度
img = img.convert('L')
# 增强对比度
img = ImageEnhance.Contrast(img).enhance(2.0)
# 二值化
img = img.point(lambda x: 0 if x < 128 else 255)
text = pytesseract.image_to_string(img, lang='<语言代码>')
print(text if text.strip() else '（未识别到文字内容）')
img.close()
"
```

#### 读取 EXIF 元数据

```bash
python -c "
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
img = Image.open(r'<图片路径>')
exif_data = img.getexif()
if not exif_data:
    print('（该图片不包含 EXIF 信息）')
else:
    for tag_id, value in exif_data.items():
        tag = TAGS.get(tag_id, tag_id)
        print(f'{tag}: {value}')
img.close()
"
```

#### 获取全部信息

```bash
python -c "
from PIL import Image
from PIL.ExifTags import TAGS
import os

path = r'<图片路径>'
img = Image.open(path)

print('=== 基本信息 ===')
print(f'文件: {os.path.basename(path)}')
print(f'大小: {os.path.getsize(path) / 1024:.1f} KB')
print(f'格式: {img.format}')
print(f'尺寸: {img.size[0]} x {img.size[1]} px')
print(f'色彩模式: {img.mode}')

print()
print('=== EXIF 元数据 ===')
exif_data = img.getexif()
if not exif_data:
    print('（无 EXIF 信息）')
else:
    for tag_id, value in exif_data.items():
        tag = TAGS.get(tag_id, tag_id)
        print(f'{tag}: {value}')

print()
print('=== OCR 文字识别 ===')
try:
    import pytesseract
    text = pytesseract.image_to_string(img, lang='chi_sim+eng')
    print(text if text.strip() else '（未识别到文字内容）')
except ImportError:
    print('（pytesseract 未安装，跳过 OCR）')
except Exception as e:
    print(f'（OCR 失败: {e}）')

img.close()
"
```

### 第三步：格式化输出

```
🖼️ 图片内容：filename.png
═══════════════════════════════════════════

=== 基本信息 ===
文件: filename.png
大小: 256.3 KB
格式: PNG
尺寸: 1920 x 1080 px
色彩模式: RGB

=== EXIF 元数据 ===
（无 EXIF 信息）

=== OCR 文字识别 ===
（识别到的文字内容）
```

---

## 注意事项

- OCR 识别率取决于图片质量，模糊、倾斜、低分辨率的图片效果较差
- 截图、扫描件等清晰图片识别效果最好
- 中文识别需要安装 `tesseract-ocr-chi-sim` 语言包
- EXIF 信息通常只存在于相机拍摄的 JPG 图片中，PNG/截图一般没有
- 大尺寸图片 OCR 可能较慢，建议裁剪关注区域后再识别
- 如果 pytesseract 未安装，仍可使用 `info` 和 `exif` 模式
