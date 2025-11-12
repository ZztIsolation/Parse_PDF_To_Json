# 源代码使用说明

## 📁 脚本说明

### 核心脚本

| 脚本 | 功能 | 用途 |
|-----|------|------|
| `split_pdf_by_courses.py` | PDF分割 | 将大PDF按课程分割成124个小PDF |
| `pdf_to_markdown.py` | Markdown转换 | 将PDF转换为Markdown格式 |
| `process_markdown.py` | 信息提取 | 从Markdown提取结构化JSON数据 |
| `test_ollama_connection.py` | 环境测试 | 测试Ollama连接和模型 |

---

## 🚀 使用流程

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 安装Ollama

访问 https://ollama.com/download 下载并安装

```bash
ollama pull qwen2.5:7b
```

### 3. 测试环境

```bash
python src/test_ollama_connection.py
```

### 4. 运行处理

```bash
# 批量处理所有Markdown文件
python src/process_markdown.py
```

---

## 📊 各脚本详细说明

### split_pdf_by_courses.py

**功能：** 按课程分割PDF

**输入：** `docs/25. 计算机科学与技术专业.pdf` (1229页)

**输出：** `docs/all/*.pdf` (124个文件)

**运行：**
```bash
python src/split_pdf_by_courses.py
```

---

### pdf_to_markdown.py

**功能：** 批量转换PDF为Markdown

**输入：** `docs/all/*.pdf` (124个文件)

**输出：** `docs/md/*.md` (124个文件)

**运行：**
```bash
python src/pdf_to_markdown.py
```

**特点：**
- 使用PyMuPDF4LLM，完全免费
- 显示实时进度条
- 约7分钟完成124个文件

---

### process_markdown.py

**功能：** 提取结构化信息

**输入：** `docs/md/*.md` (124个文件)

**输出：** `docs/json_v2/*.json` (124个文件)

**运行：**
```bash
python src/process_markdown.py
```

**提取内容：**
1. 课程名称和代码
2. 课程目标（结构化）
3. 毕业要求对应关系

**处理时间：** 约25-35分钟

---

### test_ollama_connection.py

**功能：** 测试Ollama环境

**运行：**
```bash
python src/test_ollama_connection.py
```

**检查项：**
- Ollama库是否安装
- Ollama服务是否运行
- qwen2.5:7b模型是否可用
- 模型推理是否正常

---

## ⚙️ 配置说明

### 修改输入输出路径

编辑各脚本的 `main()` 函数：

```python
# split_pdf_by_courses.py
input_pdf = "docs/你的PDF文件.pdf"
output_directory = "docs/all"

# pdf_to_markdown.py
input_dir = "docs/all"
output_dir = "docs/md"

# process_markdown.py
md_dir = "docs/md"
output_dir = "docs/json_v2"
```

---

## ❓ 常见问题

### Q1: Ollama连接失败？

**解决：** 确保Ollama服务正在运行
```bash
ollama serve
```

### Q2: 模型未找到？

**解决：** 下载模型
```bash
ollama pull qwen2.5:7b
```

### Q3: 处理速度慢？

**原因：** CPU处理速度较慢（5-10 tokens/s）

**解决：**
- 使用GPU加速（50-100+ tokens/s）
- 或使用更小的模型（qwen2.5:3b）

### Q4: JSON解析失败？

**原因：** AI输出格式不正确

**解决：**
- 检查错误日志
- 降低temperature参数
- 手动修正JSON文件

---

## � 更多信息

完整文档请查看：[../docs/项目文档.md](../docs/项目文档.md)

