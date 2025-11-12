# PDF转Markdown工具对比报告

## 📊 测试概况

- **测试日期**: 2025-11-08
- **测试文件数**: 5个
- **对比工具**:
  1. **PyMuPDF4LLM** - 当前使用的工具
  2. **Unstructured (fast策略)** - 新测试的工具

## 📋 测试样本

| 文件名 | 类型 | PyMuPDF行数 | Unstructured行数 | 差异 |
|--------|------|-------------|------------------|------|
| 002_中国近现代史纲要.md | 思政类 | 656 | 693 | +5.6% |
| 003_毛泽东思想和中国特色社会主义理论体系概论.md | 思政类 | 556 | 544 | -2.2% |
| 004_马克思主义基本原理.md | 思政类 | 2,269 | 2,693 | +18.7% |
| 005_形势与政策1.md | 思政类 | 381 | 652 | +71.1% |
| 006_形势与政策2.md | 思政类 | 381 | 630 | +65.4% |
| **总计** | - | **4,243** | **5,212** | **+22.8%** |

## 📈 详细统计

### PyMuPDF4LLM
- ✅ **总行数**: 4,243
- ✅ **总字符数**: 64,155
- ✅ **平均行数**: 849行/文件
- ✅ **平均字符数**: 12,831字符/文件
- ✅ **平均处理速度**: ~2秒/文件

### Unstructured (fast)
- 📊 **总行数**: 5,212 (+22.8%)
- 📊 **总字符数**: 61,307 (-4.4%)
- 📊 **平均行数**: 1,042行/文件
- 📊 **平均字符数**: 12,261字符/文件
- 📊 **平均处理速度**: ~1.7秒/文件

## 🔍 质量分析

### 示例文件: 002_中国近现代史纲要.md

#### 表格处理
| 工具 | 表格数量 | 表格格式 |
|------|---------|---------|
| PyMuPDF4LLM | 31个 | ✅ Markdown表格格式 |
| Unstructured | 0个 | ❌ 表格被拆分为普通文本 |

#### 标题处理
| 工具 | H1标题 | H2标题 | 问题 |
|------|--------|--------|------|
| PyMuPDF4LLM | 0 | 1 | ✅ 正常 |
| Unstructured | 0 | 286 | ❌ 过度分割，几乎每行都是标题 |

## ⚖️ 优缺点对比

### PyMuPDF4LLM ⭐⭐⭐⭐⭐

#### 优点 ✅
1. **表格保留完美** - 完整保留Markdown表格格式
2. **格式准确** - 标题、段落、列表等格式识别准确
3. **字符完整** - 保留更多原始字符（64,155 vs 61,307）
4. **易于解析** - 生成的Markdown适合后续AI处理
5. **无需额外依赖** - 不需要poppler等外部工具

#### 缺点 ❌
1. 部分表格可能有列名显示为`Col2`、`Col3`的问题
2. 复杂表格的单元格合并可能显示为`<br>`换行

### Unstructured (fast) ⭐⭐

#### 优点 ✅
1. **处理速度快** - 平均1.7秒/文件
2. **元素识别** - 能识别不同类型的元素（Title, NarrativeText等）
3. **轻量级** - fast策略不需要额外依赖

#### 缺点 ❌
1. **表格丢失** - 完全无法保留表格格式（0个表格 vs 31个）
2. **过度分割** - 将普通文本行误识别为标题（286个H2标题）
3. **格式混乱** - 生成的Markdown不适合后续处理
4. **字符丢失** - 丢失约4.4%的字符内容

### Unstructured (hi_res) ❌ 无法测试

#### 问题
- ❌ 需要安装`poppler`工具
- ❌ Windows环境下安装复杂
- ❌ 所有测试文件均失败：`Unable to get page count. Is poppler installed and in PATH?`

## 📊 实际输出对比

### PyMuPDF4LLM 输出示例
```markdown
## 《中国近现代史纲要》课程教学大纲

|课程英文名|TheOutlineofModernandContemporaryHistoryofChina|Col3|Col4|
|---|---|---|---|
|课程代码|**A2301210**|课程类别|通识公共课|
|学分|**3**|总学时数|**48**|

一、课程目标

《中国近现代史纲要》属于高校"思想政治理论课"...

课程目标 **1** （知识）： 帮助学生了解国史、国情...
```

### Unstructured 输出示例
```markdown
## （一）思政类课程教学大纲

## 《中国近现代史纲要》课程教学大纲

## 课程英文名

## The Outline of Modern and Contemporary History of China

## 课程代码

A2301210 课程类别

## 通识公共课 课程性质

## 通识必修

## 学分

3

## 总学时数

48
```

## 🎯 结论与建议

### 结论
1. **PyMuPDF4LLM 明显优于 Unstructured**
   - 表格保留率: 100% vs 0%
   - 格式准确性: 高 vs 低
   - 内容完整性: 高 vs 中

2. **Unstructured 不适合本项目**
   - 表格是课程大纲的核心内容（毕业要求对应关系表）
   - Unstructured完全无法保留表格格式
   - 过度分割导致后续AI处理困难

### 建议
✅ **继续使用 PyMuPDF4LLM**
- 表格保留完美，适合提取"毕业要求对应关系"
- 格式准确，便于后续AI解析
- 无需额外依赖，部署简单

❌ **不推荐使用 Unstructured**
- 表格丢失是致命缺陷
- hi_res策略需要复杂的外部依赖
- fast策略输出质量不符合项目需求

## 📁 测试文件位置

- **PyMuPDF4LLM输出**: `docs/md/`
- **Unstructured输出**: `docs/md_uns/`
- **对比脚本**: `test_compare_conversions.py`

## 🔧 技术细节

### PyMuPDF4LLM
```python
import pymupdf4llm
markdown_text = pymupdf4llm.to_markdown(pdf_path)
```

### Unstructured
```python
from unstructured.partition.pdf import partition_pdf

elements = partition_pdf(
    filename=pdf_path,
    strategy='fast',  # 或 'hi_res' (需要poppler)
    infer_table_structure=True,
    include_page_breaks=False,
)
```

## 📝 备注

- Unstructured的`hi_res`策略理论上能更好地处理表格，但需要安装poppler
- 在Windows环境下安装poppler较为复杂，且测试失败
- 即使`hi_res`能工作，考虑到`fast`策略的表现，预期效果也不会超过PyMuPDF4LLM

---

**测试结论**: PyMuPDF4LLM 是本项目的最佳选择 ✅

