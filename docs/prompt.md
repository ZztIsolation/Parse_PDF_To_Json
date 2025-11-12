角色: 你是一名资深的Python开发者，精通使用正则表达式（Regex）和本地小型语言模型（SLM）来构建健壮的数据提取流水线（Pipeline）。

你的目标: 为我生成一个完整、可运行的Python脚本。这个脚本将自动处理一个从PDF转换而来、格式混乱的Markdown文件（基于 061_程序设计基础.md），并精确提取三部分关键信息。

核心战略（必须遵守）： 你必须采用**“代码与AI结合”**的混合流水线策略。

代码 (Regex) - 粗切分与验证: 对于结构化、边界清晰的任务（如定位章节、验证标题、查找H1标题），必须使用Python的 re 模块。这能确保100%的准确性和速度。

AI (Ollama) - 精加工: 对于非结构化、格式混乱、需要“理解”的任务（如清理带页码的段落、从破碎的Markdown表格中提取语义），你必须使用 ollama Python库调用一个本地运行的小模型。

技术栈与假设

语言: Python 3

库: import re, import ollama

AI模型: 脚本必须调用 qwen:7b 模型（因为它轻量且中文效果好）。

假设: 用户已经安装并运行了Ollama本地服务，并且已经通过命令 ollama pull qwen:7b 拉取了模型。你的脚本必须包含 try...except 块来捕获连接Ollama失败的异常。

脚本实现细节

请生成一个包含以下所有功能的Python脚本：

1. 主要逻辑 (Main Function):

脚本应包含一个 main() 函数。

main() 函数首先从磁盘加载Markdown文件（例如，"061_程序设计基础.md"）的全部内容到 md_content 变量中。

main() 函数依次调用以下三个独立的提取函数，并打印它们的返回结果。

2. 任务一：提取课程名称 (纯代码实现)

功能: def extract_course_name(md_content):

策略: 必须使用 Regex。禁止为此任务调用AI模型。

实现:

Python

match = re.search(r'# 《(.*?)》', md_content)if match:

    return match.group(1)return "未找到课程名称"

3. 任务二：提取并清理第一章 (代码+AI混合实现)

功能: def extract_and_clean_chapter_1(md_content):

策略: 混合实现。

步骤 3.1 (Regex 粗切分):

使用Regex从 md_content 中定位并提取出“第一章”的原始、混乱的文本块。

Regex (参考): re.search(r'(一、 课程目标[\s\S]*?)二、', md_content)

步骤 3.2 (Ollama 精加工):

将上一步提取的 raw_text 块发送给 qwen:7b。

必须使用 ollama.chat()。

必须使用以下 system_prompt 和 user_prompt：

system_prompt = "你是一个文本格式化助手。你的任务是清理和重组课程大纲章节。请移除所有单独的页码（如 '534'）和不必要的换行，将正文和课程目标（如 '课程目标1'）整理成通顺、连续的中文段落和编号列表。"

user_prompt = f"请处理以下原始文本：\n\n{raw_text_from_step_3_1}"

函数返回模型清理后的 response['message']['content']。

4. 任务三：提取第二章的表格内容 (代码+AI混合实现) [已更新]

功能: def extract_chapter_2_tables(md_content):

策略: 混合实现，先用代码验证，再用AI提取。

步骤 4.1 (Regex 粗切分 - 章节):

使用Regex提取从“二、”开始到“三、”之前（或文件末尾）的整个第二章的文本块。

Regex (参考): re.search(r'(二、[\s\S]*?)(?=三、|\Z)', md_content)

如果 re.search 未找到匹配项，函数应返回 "未找到第二章内容。"。

步骤 4.2 (纯代码 - 标题验证) [关键步骤]:

获取上一步 chapter_2_block 的第一行 first_line = chapter_2_block.split('\n', 1)[0]。

检查 first_line 是否包含**“课程目标与毕业要求对应关系”**。

如果first_line不包含这个必需的标题，函数必须立即返回一个提示信息，例如：f"已跳过：第二章标题为 '{first_line.strip()}'，不是所需内容。"

步骤 4.3 (Regex 粗切分 - 表格):

仅当 4.2 验证通过后，才在此章节文本块 (chapter_2_block) 中使用 re.findall 提取出所有的Markdown表格。

Regex (参考): re.findall(r'(\|表.*?\|[\s\S]*?)(?=\n\n|\Z)', chapter_2_block)

步骤 4.4 (Ollama 循环精加工):

遍历 4.3 中找到的表格列表 table_list。

在循环内部，为每一个表格调用 ollama.chat('qwen:7b', ...)。

必须使用以下 system_prompt 和 user_prompt：

system_prompt = "你是一个表格数据提取器。请从下面的Markdown表格文本中，严格按照以下格式提取信息：1. 提取表格标题（第一行，例如 '表1 计算机科学与技术专业课程目标与毕业要求对应关系'）。2. 提取表格中**第一列**的内容（忽略'毕业要求'这个表头）。3. **如果第一列的内容有重复（例如多个'毕业要求1'），只保留第一个**。4. 输出格式必须是：[标题]: [第一列内容1]; [第一列内容2]; [第一列内容3]"

user_prompt = f"请处理以下表格文本：\n\n{current_table_string_in_loop}"

函数将所有模型返回的提取结果（例如 表1: ...; 表2: ...）收集到一个列表中并返回。

5. 错误处理:

在 main() 函数中，对Ollama的调用（任务2和3）必须包含在 try...except ollama.ResponseError 和 except Exception 块中，以捕获模型未找到或Ollama服务未运行的错误。