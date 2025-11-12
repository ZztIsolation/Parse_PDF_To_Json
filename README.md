# Parse_PDF_To_Json

将大型PDF教学大纲自动化处理为结构化JSON数据。

## 🎯 项目目标

从1229页的PDF文档中提取124门课程的结构化信息：

1. **PDF分割**: 按课程分割成124个独立PDF
2. **Markdown转换**: 转换为Markdown格式
3. **信息提取**: 使用代码+AI提取结构化数据

## 📊 处理结果

| 项目 | 数值 |
|-----|------|
| 原始PDF | 1229页 |
| 课程数量 | 124门 |
| 输出格式 | JSON |
| 处理方式 | 代码 + AI（本地） |
| 总耗时 | ~30分钟 |

## ✨ 核心特点

- ✅ 完全自动化处理
- ✅ 本地运行，无API成本
- ✅ 结构化JSON输出
- ✅ 支持多专业课程
- ✅ 高准确率（90-95%）

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 安装Ollama和模型

```bash
# 下载并安装Ollama: https://ollama.com/download
# 拉取模型
ollama pull qwen2.5:7b
```

### 3. 测试环境

```bash
python src/test_ollama_connection.py
```

### 4. 运行处理

```bash
# 批量处理所有文件
python src/process_markdown.py
```

输出文件在 `docs/json_v2/` 目录。

---

## 📖 详细文档

完整的使用说明和技术文档请查看：

👉 **[docs/项目文档.md](docs/项目文档.md)**

---

## 📁 输出示例

```
docs/json_v2/
├── A0501180_程序设计基础.json
├── A0502170_数据结构.json
├── A0503160_操作系统.json
└── ... (共124个JSON文件)
```

## 📁 项目结构

```
Parse_PDF_To_Json/
├── src/                              # 源代码
│   ├── split_pdf_by_courses.py      # PDF分割
│   ├── pdf_to_markdown.py           # Markdown转换
│   ├── process_markdown.py          # 信息提取（主要）
│   └── test_ollama_connection.py    # 环境测试
├── docs/                             # 数据和文档
│   ├── all/                          # 分割后的PDF（124个）
│   ├── md/                           # Markdown文件（124个）
│   ├── json_v2/                      # JSON输出（124个）
│   └── 项目文档.md                   # 完整文档
├── requirements.txt                  # Python依赖
└── README.md                         # 本文件
```

## 📊 提取的数据结构

每个JSON文件包含：

```json
{
  "course_name": "程序设计基础",
  "course_code": "A0501180",
  "course_goals": {
    "overview": "课程目标总述...",
    "goals": [
      {
        "number": "1",
        "content": "第一个课程目标..."
      }
    ]
  },
  "requirement_mappings": [
    {
      "major": "计算机科学与技术",
      "mappings": [
        {
          "requirement_number": "1",
          "requirement": "毕业要求1：工程知识...",
          "indicator": "1-2 掌握计算机科学核心知识...",
          "course_goals": "目标1：0.6 目标2：0.4"
        }
      ]
    }
  ]
}
```

## 🔧 技术栈

- **Python 3.8+**: 主要开发语言
- **pypdf**: PDF分割和处理
- **PyMuPDF4LLM**: PDF转Markdown
- **Ollama + qwen2.5:7b**: 本地AI模型
- **正则表达式**: 结构化信息提取

## 📞 更多信息

详细文档请查看：[docs/项目文档.md](docs/项目文档.md)

