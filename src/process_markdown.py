"""
Markdown内容处理脚本  - 简化版

只提取最重要的信息：
1. 课程名称和课程代码（AI提取）
2. 课程目标（代码定位 + AI清理）
3. 毕业要求对应关系（代码定位 + AI解析）

作者: AI Assistant
日期: 2025-01-07
"""

import os
import re
import json
import time
import requests
from datetime import datetime
from typing import Dict, List, Optional

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("⚠️ 警告: ollama库未安装，请运行: pip install ollama")

# DeepSeek API配置
DEEPSEEK_API_KEY = "sk-07210ded9e714b96befe824d8c79fde4"
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"


# ==================== 任务1: 提取课程名称和代码 (代码优先+AI辅助) ====================

def extract_course_code_with_regex(md_content: str) -> Optional[str]:
    """
    使用正则表达式提取课程代码

    Args:
        md_content: Markdown文件内容

    Returns:
        课程代码，如果未找到返回None
    """
    # 模式1: **A2301210** (加粗，标准格式：1个大写字母+7位数字)
    pattern1 = r'\*\*([A-Z]\d{7})\*\*'
    match = re.search(pattern1, md_content)
    if match:
        return match.group(1)

    # 模式2: |课程代码|A2301210| (表格中，标准格式)
    pattern2 = r'\|课程(?:代码|编号)\|([A-Z]\d{7})\|'
    match = re.search(pattern2, md_content)
    if match:
        return match.group(1)

    # 模式3: **A051201s** (加粗，非标准格式：可能有小写字母后缀)
    pattern3 = r'\*\*([A-Z][A-Za-z0-9]{6,8})\*\*'
    match = re.search(pattern3, md_content)
    if match:
        code = match.group(1)
        # 验证至少有6个字符
        if len(code) >= 7:
            return code

    # 模式4: |课程代码|A051201s| (表格中，非标准格式)
    pattern4 = r'\|课程(?:代码|编号)\|([A-Z][A-Za-z0-9]{6,8})\|'
    match = re.search(pattern4, md_content)
    if match:
        code = match.group(1)
        if len(code) >= 7:
            return code

    return None


def extract_course_name_with_regex(md_content: str) -> Optional[str]:
    """
    使用正则表达式提取课程名称

    Args:
        md_content: Markdown文件内容

    Returns:
        课程名称，如果未找到返回None
    """
    # 模式1: # 《课程名》课程教学大纲
    pattern1 = r'#\s*《(.*?)》'
    match = re.search(pattern1, md_content)
    if match:
        return match.group(1).strip()

    # 模式2: ## 《课程名》课程教学大纲
    pattern2 = r'##\s*《(.*?)》'
    match = re.search(pattern2, md_content)
    if match:
        return match.group(1).strip()

    return None


def extract_course_basic_info_with_ai(md_content: str, model: str = 'qwen2.5:7b') -> Dict[str, str]:
    """
    使用AI提取课程名称和课程代码
    
    Args:
        md_content: Markdown文件内容
        model: 使用的AI模型
        
    Returns:
        包含course_name和course_code的字典
    """
    # 只提取前800行，包含课程基本信息
    lines = md_content.split('\n')[:800]
    header_text = '\n'.join(lines)
    
    system_prompt = """你是一个专业的课程信息提取助手。

任务：从课程教学大纲的Markdown文本中提取课程名称和课程代码。

提取规则：
1. 课程名称：
   - 通常在标题中，格式如：# 《课程名》课程教学大纲 或 ## 《课程名》课程教学大纲
   - 提取《》中的内容，**必须保留完整的课程名称，包括数字、空格、括号等所有字符**
   - 例如："《大学物理 1》" → "大学物理 1"（保留空格和数字）
   - 例如："《大学物理2》" → "大学物理2"（保留数字）
   - 例如："《物理学原理及工程应用1》" → "物理学原理及工程应用1"（保留数字）
   - 如果没有《》，提取标题中的课程名称部分
   - 不要包含"课程教学大纲"这几个字
   - **不要删除或修改课程名称中的任何字符**

2. 课程代码：
   - 标准格式：1个大写字母 + 7位数字，如：A2301210、S0718060、A0501180
   - 非标准格式：可能有小写字母后缀，如：A051201s、ETH01
   - 在表格中，标注为"课程编号"、"课程代码"、"课程代码"等
   - 通常用**加粗**标记，如：**A2301210**、**A051201s**
   - 注意：不是学分、学时等其他数字
   - 长度通常在7-9个字符之间

示例1：
输入：|课程代码|**A2301210**|课程类别|通识公共课|
输出：{"course_name": "...", "course_code": "A2301210"}

示例2：
输入：|课程代码|**A051201s**|课程类别|学科基础课|
输出：{"course_name": "...", "course_code": "A051201s"}

重要：
- 只输出JSON，不要输出其他任何内容
- 不要输出课程目标、学时分配等其他信息
- 只输出course_name和course_code两个字段
- 接受非标准格式的课程代码（如带小写字母后缀）

输出格式：
{
  "course_name": "课程名称",
  "course_code": "课程代码"
}

如果找不到，对应字段填写"未找到"。
"""
    
    user_prompt = f"""请从以下文本中提取课程名称和课程代码：

{header_text}

只输出JSON，格式：{{"course_name": "...", "course_code": "..."}}"""
    
    try:
        response = ollama.chat(
            model=model,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            options={
                'temperature': 0.1,  # 低温度，更确定性的输出
            }
        )
        
        result_text = response['message']['content'].strip()
        
        # 尝试解析JSON
        # 移除可能的markdown代码块标记
        result_text = re.sub(r'```json\s*', '', result_text)
        result_text = re.sub(r'```\s*', '', result_text)
        
        result = json.loads(result_text)
        
        return {
            'course_name': result.get('course_name', '未找到'),
            'course_code': result.get('course_code', '未找到')
        }
        
    except json.JSONDecodeError as e:
        print(f"      ⚠️  JSON解析失败: {e}")
        print(f"      原始响应: {result_text[:200]}...")
        return {
            'course_name': '未找到',
            'course_code': '未找到',
            'raw_response': result_text
        }
    except Exception as e:
        print(f"      ⚠️  AI调用失败: {e}")
        return {
            'course_name': '未找到',
            'course_code': '未找到',
            'error': str(e)
        }


# ==================== 任务2: 提取并清理课程目标 (代码+AI) ====================

def extract_chapter_1_raw(md_content: str) -> Optional[str]:
    """
    使用正则表达式定位"一、课程目标"章节

    Args:
        md_content: Markdown文件内容

    Returns:
        第一章的原始内容，如果未找到返回None
    """
    # 匹配从"一、 课程目标"到"二、"之前的所有内容
    # 增加更多截断条件：
    # - "二、" - 标准的第二章
    # - "三、" - 如果没有第二章，可能直接到第三章
    # - "课\n\n程内容与基本要求" - PDF转换时断行的"课程内容与基本要求"
    # - "教学内容" - 教学内容章节
    # - "教学方法" - 教学方法章节
    pattern = r'(一、\s*课程目标[\s\S]*?)(?=二、|三、|课\s*\n+\s*程内容与基本要求|教学内容|教学方法|$)'
    match = re.search(pattern, md_content)

    if match:
        return match.group(1).strip()
    return None


def clean_chapter_1_with_ai(raw_text: str, model: str = 'qwen2.5:7b') -> Dict:
    """
    使用AI清理课程目标文本并结构化

    Args:
        raw_text: 原始的课程目标文本
        model: 使用的AI模型

    Returns:
        结构化的课程目标数据
    """
    system_prompt = """你是一个专业的文本清理和结构化助手。

任务：将课程目标文本清理并结构化为JSON格式。

清理和提取规则：
1. 提取总述（overview）：
   - 提取"一、课程目标"标题后、第一个具体课程目标之前的所有内容
   - 删除页码（如 "534"、"721"）
   - 合并被打断的句子
   - 删除多余空行
   - 包括课程背景、意义、"本课程拟通过教学活动，达到以下课程目标："等引导性文字

2. 提取具体课程目标（goals）：
   - 识别所有编号的课程目标（如"课程目标1"、"课程目标 **1**"、"1."等）
   - 提取目标编号（number）：只提取数字，如"1"、"2"、"3"
   - 提取目标内容（content）：提取冒号或句号后的完整描述
   - 删除页码、合并被打断的句子、删除多余空行
   - 保留所有实质性内容，不要总结或删减

输出格式：
严格按照JSON格式输出：
{
  "overview": "课程目标的总述部分",
  "goals": [
    {
      "number": "1",
      "content": "第一个课程目标的完整内容"
    },
    {
      "number": "2",
      "content": "第二个课程目标的完整内容"
    }
  ]
}

注意：
- 只输出JSON，不要输出其他任何内容
- 如果没有总述部分，overview为空字符串
- 如果没有具体目标，goals为空数组
"""

    user_prompt = f"""请清理并结构化以下课程目标文本：

{raw_text}

请严格按照JSON格式输出。"""

    try:
        response = ollama.chat(
            model=model,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            options={
                'temperature': 0.1,
            }
        )

        result_text = response['message']['content'].strip()

        # 移除markdown代码块标记
        result_text = re.sub(r'```json\s*', '', result_text)
        result_text = re.sub(r'```\s*', '', result_text)

        result = json.loads(result_text)
        return result

    except json.JSONDecodeError as e:
        print(f"      ⚠️  JSON解析失败")
        # 返回原始文本作为overview
        return {
            'overview': raw_text,
            'goals': []
        }
    except Exception as e:
        print(f"      ⚠️  AI清理失败: {e}")
        # 返回原始文本作为overview
        return {
            'overview': raw_text,
            'goals': []
        }


# ==================== 任务3: 提取毕业要求对应关系 (代码+AI) ====================

def extract_chapter_2_raw(md_content: str) -> Optional[str]:
    """
    使用正则表达式定位"二、..."章节
    
    Args:
        md_content: Markdown文件内容
        
    Returns:
        第二章的原始内容，如果未找到返回None
    """
    # 匹配从"二、"到"三、"之前的所有内容
    pattern = r'(二、[\s\S]*?)(?=三、|$)'
    match = re.search(pattern, md_content)
    
    if match:
        return match.group(1).strip()
    return None


def validate_chapter_2_title(chapter_2_text: str) -> bool:
    """
    验证第二章是否是关于"课程目标与毕业要求对应关系"，并且包含实际内容

    Args:
        chapter_2_text: 第二章的文本

    Returns:
        是否是对应关系章节且包含有效内容
    """
    # 步骤1：检查标题中是否包含关键词
    first_line = chapter_2_text.split('\n')[0]
    keywords = ['课程目标', '毕业要求', '对应关系']
    if not all(keyword in first_line for keyword in keywords):
        return False

    # 步骤2：检查内容是否明确说明"不做描述"或"无"
    # 这些课程虽然有标题，但实际上没有对应关系表格
    skip_patterns = [
        '不做描述',
        '此不做描述',
        '不作描述',
        '各专业毕业要求各异',
        '因各专业.*不做描述',
        '暂无',
        '^无$',
        '^无。$',
    ]

    # 获取标题后的内容（前200个字符足够判断）
    content_after_title = '\n'.join(chapter_2_text.split('\n')[1:])[:200]

    for pattern in skip_patterns:
        if re.search(pattern, content_after_title):
            return False

    # 步骤3：检查是否包含表格标记（|符号）
    # 如果标题正确但完全没有表格，也应该跳过
    if '|' not in chapter_2_text:
        return False

    return True


def extract_tables_raw(chapter_2_text: str) -> List[str]:
    """
    从第二章中提取所有表格

    Args:
        chapter_2_text: 第二章的文本

    Returns:
        表格文本列表
    """
    tables = []

    # 模式1: 匹配以"表X"或"表 X"开头的表格（包括"表 **1-1**"这种格式）
    # 匹配从"表"开始，到下一个"表"或"三、"或文件结尾
    # 注意：这里要匹配"表"开头的行，包括前面可能有的文字（如"如表 1 所示"）
    pattern1 = r'((?:.*表\s*[\*\d\-]+.*\n)[\s\S]*?\|[\s\S]*?)(?=\n\n+.*表\s*[\*\d\-]+|\n\n+三、|\Z)'
    matches1 = re.finditer(pattern1, chapter_2_text)

    for match in matches1:
        table_text = match.group(1).strip()
        # 确保是表格（包含|符号）且包含"毕业要求"关键词
        if '|' in table_text and ('毕业要求' in table_text or '指标点' in table_text or '课程目标' in table_text):
            tables.append(table_text)

    return tables


def preprocess_table(table_text: str) -> str:
    """
    预处理表格，修复异常格式

    问题1：有些表格的标题被嵌入到表格的第一行中，例如：
    表

    1 所示。

    |表1 计算机科学与技术专业课程|程目标与毕业要求对应关系|Col3|
    |---|---|---|
    |毕业要求|指标点|课程目标|

    问题2：有些表格的标题被断成多行，例如：
    表 5 智能硬件与系统专业课程目标与毕业要求对


    应关系

    解决：
    1. 检测并合并断行的标题
    2. 检测并提取嵌入表格的标题
    3. 重构表格，删除无关文字

    Args:
        table_text: 原始表格文本

    Returns:
        预处理后的表格文本
    """
    lines = table_text.split('\n')

    if len(lines) < 3:
        return table_text

    # ============================================================
    # 步骤1：合并断行的标题
    # ============================================================
    # 检测特征：
    # - 某一行以"对"、"关"、"系"等字结尾（标题的一部分）
    # - 后面有若干空行
    # - 再后面有一行以"应"、"系"、"表"等字开头（标题的另一部分）
    #
    # 示例：
    # "...毕业要求对\n\n\n应关系" → "...毕业要求对应关系"
    # "...课程目标与毕业要求对\n\n应关系" → "...课程目标与毕业要求对应关系"

    # 常见的断行模式
    title_break_patterns = [
        (r'对$', r'^应'),      # "对" + "应" → "对应"
        (r'关$', r'^系'),      # "关" + "系" → "关系"
        (r'对$', r'^应关系'),  # "对" + "应关系" → "对应关系"
        (r'要求$', r'^对应'),  # "要求" + "对应" → "要求对应"
    ]

    # 尝试合并断行
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # 跳过空行和表格行
        if not line or line.startswith('|'):
            i += 1
            continue

        # 检查是否包含"表"字（可能是标题）
        if '表' in line and ('专业' in line or '课程' in line or '毕业要求' in line):
            # 检查是否匹配断行模式
            for end_pattern, start_pattern in title_break_patterns:
                if re.search(end_pattern, line):
                    # 查找后续的非空行（跳过空行）
                    j = i + 1
                    while j < len(lines) and not lines[j].strip():
                        j += 1

                    if j < len(lines):
                        next_line = lines[j].strip()
                        # 检查下一个非空行是否匹配开始模式
                        if re.search(start_pattern, next_line) and not next_line.startswith('|'):
                            # 找到断行！合并它们
                            merged_line = line + next_line

                            # 替换原来的行
                            lines[i] = merged_line

                            # 删除中间的空行和下一行
                            del lines[i+1:j+1]

                            # 不增加i，继续检查当前行（可能有多次断行）
                            break
            else:
                # 没有匹配任何模式，继续下一行
                i += 1
        else:
            i += 1

    # 重新组合文本
    table_text = '\n'.join(lines)

    # ============================================================
    # 步骤2：查找独立的标题行（优先级最高）
    # ============================================================
    # 在表格前查找独立的标题行，例如：
    # "表 **3** 课程目标与计算机科学英才班（计算机科学与技术）专业毕业要求对应关系"

    independent_title = None
    independent_title_idx = -1

    # 找到第一个表格行（以|开头）
    first_table_line_idx = -1
    for i, line in enumerate(lines):
        if line.strip().startswith('|'):
            first_table_line_idx = i
            break

    if first_table_line_idx == -1:
        return table_text

    # 在表格前查找独立的标题行
    # 特征：包含"表"、"课程目标"、"专业"、"毕业要求"、"对应关系"
    for i in range(max(0, first_table_line_idx - 10), first_table_line_idx):
        line = lines[i].strip()
        if (line and
            not line.startswith('|') and
            '表' in line and
            '课程目标' in line and
            ('专业' in line or '毕业要求' in line) and
            '对应关系' in line):
            # 找到独立的标题行
            independent_title = line
            independent_title_idx = i
            break

    # ============================================================
    # 步骤3：处理标题嵌入表格第一行的情况
    # ============================================================

    # 提取第一个表格行的单元格
    first_table_line = lines[first_table_line_idx].strip()
    cells = [cell.strip() for cell in first_table_line.split('|') if cell.strip()]

    # 检查第一个单元格是否包含"表"字（表格标题的特征）
    if len(cells) >= 2 and '表' in cells[0] and ('专业' in cells[0] or '课程' in cells[0]):
        # 这是一个异常格式的表格，标题在表格的第一行

        # 如果找到了独立的标题行，优先使用它
        if independent_title:
            title = independent_title
        else:
            # 没有独立标题，从表格第一行提取
            # 过滤掉无意义的列（如"Col3"、"Col2"等）
            meaningful_cells = []
            for cell in cells:
                # 跳过"ColX"这种列
                if re.match(r'^Col\d+$', cell, re.IGNORECASE):
                    continue
                meaningful_cells.append(cell)

            # 合并有意义的单元格作为标题
            # 智能合并：如果前一个单元格以某个字结尾，后一个单元格以同一个字开头，则去掉重复
            title_parts = []
            for i, cell in enumerate(meaningful_cells):
                if i == 0:
                    title_parts.append(cell)
                else:
                    prev_cell = title_parts[-1]
                    # 检查是否有重复字符（如"课程" + "程目标" → "课程目标"）
                    merged = False
                    for overlap_len in range(min(3, len(prev_cell), len(cell)), 0, -1):
                        if prev_cell[-overlap_len:] == cell[:overlap_len]:
                            # 有重复，合并时去掉重复部分
                            title_parts[-1] = prev_cell + cell[overlap_len:]
                            merged = True
                            break
                    if not merged:
                        title_parts.append(cell)

            title = ''.join(title_parts)

        # 检查下一行是否是分隔符行（---|---|---）
        if first_table_line_idx + 1 < len(lines) and '---' in lines[first_table_line_idx + 1]:
            # 删除标题行和分隔符行，保留表头和数据行
            #
            # 表格结构：
            # first_table_line_idx:     |表1 xxx|xxx|Col3|  <- 标题行（要删除）
            # first_table_line_idx + 1: |---|---|---|       <- 分隔符行（要删除）
            # first_table_line_idx + 2: |毕业要求|指标点|课程目标|  <- 表头行（要保留）
            # first_table_line_idx + 3: |数据1|数据2|数据3|  <- 数据行（要保留）

            # 从表头行开始保留（first_table_line_idx + 2）
            remaining_table = lines[first_table_line_idx + 2:]

            # 检查是否有下一个表格（以|表X开头的行）
            # 如果有，在那里截断
            table_end_idx = len(remaining_table)
            for i, line in enumerate(remaining_table):
                # 检查是否是另一个表格的标题行
                # 特征：以|开头，包含"表"字，包含"专业"或"课程目标"（完整词），且包含"对应关系"
                # 排除表头行（如"|毕业要求|指标点|课程目标|"）
                if (line.strip().startswith('|') and
                    '表' in line and
                    ('专业' in line or '课程目标' in line) and
                    '对应关系' in line):
                    table_end_idx = i
                    break

            # 只保留到下一个表格之前的内容
            remaining_table = remaining_table[:table_end_idx]

            # 重新构建：标题 + 空行 + 表头和数据行
            new_lines = [title, ''] + remaining_table
            new_table = '\n'.join(new_lines)

            return new_table

    return table_text


def parse_table_with_ai(table_text: str, model: str = 'qwen2.5:7b') -> Dict:
    """
    使用AI解析表格

    Args:
        table_text: 表格的Markdown文本
        model: 使用的AI模型

    Returns:
        解析后的结构化数据
    """
    system_prompt = """你是一个专业的表格解析和文本清理助手。

任务：解析课程目标与毕业要求对应关系表格，并清理文本格式问题。

解析规则：
1. 提取表格标题（如"表1 计算机科学与技术专业课程目标与毕业要求对应关系"）
2. 提取专业名称（从标题中提取，去掉"专业"二字，但必须保留括号及括号内的所有内容）
   - 例如："计算机科学与技术专业" → "计算机科学与技术"
   - 例如："软件工程专业" → "软件工程"
   - 例如："计算机科学英才班（计算机科学与技术）专业" → "计算机科学英才班（计算机科学与技术）"
   - 例如："软件工程（卓越工程师班）专业" → "软件工程（卓越工程师班）"
   - 例如："计算机科学与技术（国际班）专业" → "计算机科学与技术（国际班）"
   - 重要：括号及括号内的内容是专业名称的一部分，必须完整保留，不要删除或简化
3. 解析表格内容，提取每一行的：
   - 毕业要求编号（如"1"、"2"、"6"等，从"毕业要求1："或"1.工程知识"中提取）
   - 毕业要求内容（第1列，完整内容）
   - 指标点（第2列）
   - 课程目标（第3列）

文本清理规则（非常重要）：
1. 删除所有<br>标签
2. 智能合并被<br>打断的内容：
   - "1<br>-<br>1" → "1-1"
   - "1 1" → "1-1"（如果是指标点编号）
   - "自然科<br>学" → "自然科学"
   - "工程问<br>题" → "工程问题"
3. 删除词语中间不自然的空格：
   - "基础 知识" → "基础知识"
   - "典 型环节" → "典型环节"
   - "逻辑思维分析方法 用于" → "逻辑思维分析方法用于"
4. 修正数字格式：
   - "0 .5" → "0.5"
   - "0. 4" → "0.4"
5. 保留有意义的空格：
   - "目标1：0.5 目标2：0.5" 中的空格保留
   - 句子之间的空格保留
6. 删除多余的标点符号：
   - "。<br>、<br>" → ""
   - "、<br>，<br>" → "、"

输出格式：
严格按照JSON格式输出：
{
  "table_title": "表格标题",
  "major": "专业名称（不含'专业'二字）",
  "mappings": [
    {
      "requirement_number": "毕业要求编号（如'1'、'2'）",
      "requirement": "毕业要求内容",
      "indicator": "指标点内容",
      "course_goals": "课程目标内容"
    }
  ]
}

示例：
输入："毕业要求 1 工程知识 ：能够将数学与自然科<br>学 工程学科..."
输出：{"requirement_number": "1", "requirement": "毕业要求1工程知识：能够将数学与自然科学工程学科..."}

输入："1 1 能够将数学和自然科学的基础<br>知识 逻辑思维..."
输出：{"indicator": "1-1 能够将数学和自然科学的基础知识逻辑思维..."}

输入："目标1：0 .5<br>目标2：0 .5"
输出：{"course_goals": "目标1：0.5 目标2：0.5"}
"""
    
    user_prompt = f"""请解析以下表格：

{table_text}

请严格按照JSON格式输出。"""
    
    try:
        response = ollama.chat(
            model=model,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            options={
                'temperature': 0.1,
            }
        )
        
        result_text = response['message']['content'].strip()
        
        # 移除markdown代码块标记
        result_text = re.sub(r'```json\s*', '', result_text)
        result_text = re.sub(r'```\s*', '', result_text)
        
        result = json.loads(result_text)
        return result
        
    except json.JSONDecodeError as e:
        print(f"         ⚠️  JSON解析失败")
        return {
            'table_title': '解析失败',
            'major': '未知',
            'mappings': [],
            'raw_text': table_text[:500],
            'error': str(e)
        }
    except Exception as e:
        print(f"         ⚠️  AI解析失败: {e}")
        return {
            'table_title': '解析失败',
            'major': '未知',
            'mappings': [],
            'raw_text': table_text[:500],
            'error': str(e)
        }


# ==================== 任务4: 提取课程联系 (代码定位+AI清理) ====================

def extract_course_relations_raw(md_content: str) -> Optional[str]:
    """
    使用正则表达式定位"与其它课程的联系"章节

    Args:
        md_content: Markdown文件内容

    Returns:
        原始章节文本，如果未找到返回None
    """
    # 匹配章节标题：可能是"三、"、"四、"、"五、"等
    # 匹配到下一个章节标题为止
    pattern = r'([一二三四五六七八九十]+、?\s*与其[它他]课程的联系.*?)(?=[一二三四五六七八九十]+、|\Z)'

    match = re.search(pattern, md_content, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()

    return None


def clean_course_relations_with_ai(raw_text: str, model: str = 'qwen2.5:7b') -> Dict:
    """
    使用AI清理和结构化课程联系信息

    Args:
        raw_text: 原始章节文本
        model: 使用的AI模型

    Returns:
        结构化的课程联系数据
    """
    system_prompt = """你是一个专业的文本清理和结构化助手。

任务：提取和清理"与其它课程的联系"章节中的先修课程和后续课程信息。

提取规则：
1. 识别"先修课程"（也可能是"先修课"、"前置课程"等）
2. 识别"后续课程"（也可能是"后修课程"、"后续课"等）
3. 提取课程名称列表

文本清理规则：
1. 删除所有<br>标签
2. 删除页码和多余空行
3. 删除不自然的空格：
   - "程序 设计" → "程序设计"
   - "数据 结构" → "数据结构"
4. 统一分隔符：
   - 将"、"、"，"、"；"统一为"、"
5. 删除"无"、"无。"等无意义内容
6. 如果没有明确的先修/后续课程标签，但有描述性文字，提取到description字段

输出格式：
严格按照JSON格式输出：
{
  "prerequisite_courses": ["课程1", "课程2"],
  "subsequent_courses": ["课程1", "课程2"],
  "description": "其他描述性文字（如果有）"
}

示例1：
输入：
先修课程： 程序设计基础、离散数学。
后续课程： 数据库系统、操作系统、编译原理。

输出：
{
  "prerequisite_courses": ["程序设计基础", "离散数学"],
  "subsequent_courses": ["数据库系统", "操作系统", "编译原理"],
  "description": ""
}

示例2：
输入：
先修课程： 无；
后续课程： 面向对象程序设计（C++）、面向对象程序设计（Java）。

输出：
{
  "prerequisite_courses": [],
  "subsequent_courses": ["面向对象程序设计（C++）", "面向对象程序设计（Java）"],
  "description": ""
}

示例3：
输入：
本课程与中国近现代史纲要，思想道德修养与法律基础，毛泽东思想和中国特色社会主义理论体系概论以及马克思主义基本原理概论课程互为支撑，共同协作，以达成教学目标的要求。

输出：
{
  "prerequisite_courses": [],
  "subsequent_courses": [],
  "description": "本课程与中国近现代史纲要、思想道德修养与法律基础、毛泽东思想和中国特色社会主义理论体系概论以及马克思主义基本原理概论课程互为支撑，共同协作，以达成教学目标的要求。"
}
"""

    user_prompt = f"""请提取和清理以下文本中的课程联系信息：

{raw_text}

请严格按照JSON格式输出。"""

    try:
        response = ollama.chat(
            model=model,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            options={
                'temperature': 0.1,
            }
        )

        result_text = response['message']['content'].strip()

        # 移除markdown代码块标记
        result_text = re.sub(r'```json\s*', '', result_text)
        result_text = re.sub(r'```\s*', '', result_text)

        result = json.loads(result_text)
        return result

    except json.JSONDecodeError as e:
        print(f"         ⚠️  JSON解析失败")
        return {
            "prerequisite_courses": [],
            "subsequent_courses": [],
            "description": raw_text[:200]  # 保留前200字符作为备份
        }
    except Exception as e:
        print(f"         ⚠️  AI处理失败: {str(e)}")
        return {
            "prerequisite_courses": [],
            "subsequent_courses": [],
            "description": ""
        }


# ==================== 两级处理策略 ====================
# Level 1: 表格提取 + 预处理 + AI解析（本地Ollama qwen2.5:7b）
# Level 2: 整章处理 + DeepSeek增强版prompt（DeepSeek API）

def is_parsing_failed(mappings: List[Dict]) -> bool:
    """
    判断解析是否失败

    Args:
        mappings: requirement_mappings列表

    Returns:
        True表示解析失败，需要重试
    """
    # 条件1：没有提取到任何表格
    if len(mappings) == 0:
        return True

    # 条件2：所有表格的mappings都为空
    if all(len(table.get('mappings', [])) == 0 for table in mappings):
        return True

    # 条件3：有"解析失败"或"error"的表格
    if any('error' in table or table.get('table_title') == '解析失败' for table in mappings):
        return True

    # 条件4：表格数量异常少（少于2个可能有问题）
    valid_tables = [t for t in mappings if len(t.get('mappings', [])) > 0]
    if len(valid_tables) < 2:
        return True

    return False


def parse_full_chapter_with_deepseek(chapter_text: str) -> List[Dict]:
    """
    Level 2: 使用DeepSeek API处理整个第二章（增强版prompt，包含详细示例）

    Args:
        chapter_text: 第二章的完整文本

    Returns:
        表格列表
    """
    system_prompt = """你是一个专业的课程大纲解析助手。这是一个复杂的任务，需要你仔细处理各种格式问题。

任务：从课程教学大纲的第二章中提取所有专业的毕业要求对应关系表格。

=== 关键挑战和解决方法 ===

1. 表格标题识别（最重要！）：

   错误示例1：标题嵌入在表格第一行且被截断
   原始文本：|表2 软件工程专业课程目标|标与毕业要求对应关系|Col3|
   正确处理：合并为 "表2 软件工程专业课程目标与毕业要求对应关系"

   错误示例2：提取了描述性文字
   原始文本：课程目标与相关毕业要求及其指标点的对应关系如表 6 所示。
   错误输出：table_title: "课程目标与相关毕业要求及其指标点的对应关系如表 6 所示。"
   正确处理：这不是标题！应该继续寻找真正的表格标题（如：表6 智能制造（机械类）专业...）

   标准格式：表X XXX专业课程目标与毕业要求对应关系

2. 专业名称提取（必须与标题一致！）：

   示例1：
   标题：表2 软件工程专业课程目标与毕业要求对应关系
   正确：major: "软件工程"
   错误：major: "智能计算与数据科学"（这是另一个表格的专业）

   示例2：
   标题：表6 智能制造（机械类）专业课程目标与毕业要求对应关系
   正确：major: "智能制造（机械类）"
   错误：major: "人工智能安全（网络空间安全类）"（这是另一个表格的专业）

   示例3：
   标题：表3 智能计算与数据科学（计算机科学与技术）专业...
   正确：major: "智能计算与数据科学（计算机科学与技术）"

   验证方法：检查数据内容中的专业描述是否与major一致

3. 表格内容处理：

   - 跨页分割的表格行需要合并
   - 格式错误修复：
     * "3 1" → "3-1"
     * "1.1" 或 "1-2" 都是有效的requirement_number格式
     * "目标5 03" → "目标5：0.3"
     * "目标3 06 目标4 04" → "目标3：0.6 目标4：0.4"
     * "0 .7" → "0.7"
     * "毕业要求1：工程知识：..." → requirement_number: "1"
     * "毕业要求1-2：..." → requirement_number: "1-2"

4. 数据一致性验证（关键！）：

   检查点：
   - table_title中的专业名称 = major字段
   - major字段 = mappings中的专业描述

   示例：
   如果table_title是"表2 软件工程专业..."
   那么major必须是"软件工程"
   并且mappings中的requirement应该提到"软件工程"（不是"智能计算"或其他专业）

=== 输出格式 ===

JSON数组，按照表格在文档中出现的顺序（表1、表2、表3...）：

[
  {
    "table_title": "表1 计算机科学与技术专业课程目标与毕业要求对应关系",
    "major": "计算机科学与技术",
    "mappings": [
      {
        "requirement_number": "1-2",
        "requirement": "工程知识：掌握数学、自然科学、工程基础、计算机专业领域的知识...",
        "indicator": "掌握计算机科学核心知识与理论，能够针对计算机领域复杂工程问题建立模型...",
        "course_goals": "目标1：0.6 目标2：0.4"
      }
    ]
  },
  {
    "table_title": "表2 软件工程专业课程目标与毕业要求对应关系",
    "major": "软件工程",
    "mappings": [...]
  }
]

=== 重要提醒 ===

- 只输出JSON数组，不要输出其他任何内容
- 确保每个表格都有完整的mappings
- 如果某个表格无法解析，跳过它
- 仔细核对table_title和major的一致性
- 按照表格编号顺序输出（表1、表2、表3...）
"""

    user_prompt = f"""请从以下第二章内容中提取所有专业的毕业要求对应关系表格。

特别注意：
1. 仔细识别每个表格的真实标题（不要被描述性文字误导）
2. 确保table_title和major字段一致
3. 按照表格编号顺序输出

{chapter_text}

只输出JSON数组，格式如上所述。"""

    try:
        response = requests.post(
            DEEPSEEK_API_URL,
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.1
            },
            timeout=120
        )

        if response.status_code != 200:
            print(f"         ⚠️  DeepSeek API错误: {response.status_code}")
            return []

        result_json = response.json()
        result_text = result_json['choices'][0]['message']['content'].strip()

        # 移除markdown代码块标记
        result_text = re.sub(r'```json\s*', '', result_text)
        result_text = re.sub(r'```\s*', '', result_text)

        result = json.loads(result_text)

        # 确保返回的是列表
        if isinstance(result, dict):
            result = [result]

        return result

    except Exception as e:
        print(f"         ⚠️  Level 3处理失败: {str(e)}")
        return []


# ==================== 主处理流程 ====================

def process_single_file(md_file_path: str, model: str = 'qwen2.5:7b') -> Dict:
    """
    处理单个Markdown文件
    
    Args:
        md_file_path: Markdown文件路径
        model: 使用的AI模型
        
    Returns:
        处理结果字典
    """
    # 读取文件
    with open(md_file_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    result = {
        'file_name': os.path.basename(md_file_path),
        'processed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # 任务1: 提取课程名称和代码（代码优先+AI辅助）
    print("      [1/4] 提取课程名称和代码...")

    # 先用代码提取
    course_name_regex = extract_course_name_with_regex(md_content)
    course_code_regex = extract_course_code_with_regex(md_content)

    # 如果代码提取失败，使用AI
    if not course_name_regex or not course_code_regex:
        print("           代码提取不完整，使用AI辅助...")
        course_info_ai = extract_course_basic_info_with_ai(md_content, model)
        result['course_name'] = course_name_regex or course_info_ai['course_name']
        result['course_code'] = course_code_regex or course_info_ai['course_code']
    else:
        result['course_name'] = course_name_regex
        result['course_code'] = course_code_regex

    # 任务2: 提取并清理课程目标（代码+AI）
    print("      [2/4] 提取课程目标...")
    chapter_1_raw = extract_chapter_1_raw(md_content)
    if chapter_1_raw:
        result['course_goals'] = clean_chapter_1_with_ai(chapter_1_raw, model)
    else:
        result['course_goals'] = "未找到课程目标章节"

    # 任务3: 提取毕业要求对应关系（三级处理策略）
    print("      [3/4] 提取毕业要求对应关系...")
    chapter_2_raw = extract_chapter_2_raw(md_content)

    if chapter_2_raw and validate_chapter_2_title(chapter_2_raw):
        # Level 1: 当前方法（表格提取 + 预处理 + AI）
        tables = extract_tables_raw(chapter_2_raw)
        print(f"           Level 1: 找到 {len(tables)} 个表格")

        mappings = []
        for i, table_text in enumerate(tables, 1):
            print(f"           解析表格 {i}/{len(tables)}...", end=' ')
            # 预处理表格，修复异常格式
            preprocessed_table = preprocess_table(table_text)
            parsed = parse_table_with_ai(preprocessed_table, model)
            mappings.append(parsed)
            print("✅")

        result['requirement_mappings'] = mappings

        # 检查Level 1是否失败
        if is_parsing_failed(mappings):
            print("           ⚠️  Level 1解析失败，尝试Level 2（整章处理-DeepSeek）...")

            # Level 2: 整章处理（DeepSeek增强版prompt）
            mappings_level2 = parse_full_chapter_with_deepseek(chapter_2_raw)

            if mappings_level2 and not is_parsing_failed(mappings_level2):
                print("           ✅ Level 2成功！")
                result['requirement_mappings'] = mappings_level2
            else:
                print("           ❌ Level 2仍然失败，保留Level 1结果")
                # 保留Level 1的结果（即使失败）
    else:
        result['requirement_mappings'] = []

    # 任务4: 提取课程联系（代码+AI）
    print("      [4/4] 提取课程联系...")
    course_relations_raw = extract_course_relations_raw(md_content)
    if course_relations_raw:
        result['course_relations'] = clean_course_relations_with_ai(course_relations_raw, model)
    else:
        result['course_relations'] = {
            "prerequisite_courses": [],
            "subsequent_courses": [],
            "description": ""
        }

    return result


def process_all_markdown_files(input_dir='docs/md', output_dir='docs/json', 
                                model='qwen2.5:7b', skip_existing=False):
    """
    批量处理所有Markdown文件
    
    Args:
        input_dir: 输入目录
        output_dir: 输出目录
        model: 使用的AI模型
        skip_existing: 是否跳过已存在的JSON文件
    """
    if not OLLAMA_AVAILABLE:
        print("❌ ollama库未安装，无法继续")
        return
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取所有Markdown文件
    md_files = sorted([f for f in os.listdir(input_dir) 
                      if f.endswith('.md') and f != '转换质量评估.md'])
    
    print("="*70)
    print(f"📚 找到 {len(md_files)} 个Markdown文件")
    print(f"🤖 使用模型: {model}")
    print(f"📁 输出目录: {output_dir}")
    print("="*70)
    
    success_count = 0
    failed_count = 0
    skipped_count = 0
    start_time = time.time()
    
    for i, md_file in enumerate(md_files, 1):
        md_path = os.path.join(input_dir, md_file)
        
        # 计算进度和时间
        elapsed = time.time() - start_time
        if i > 1:
            avg_time = elapsed / (i - 1)
            eta = avg_time * (len(md_files) - i + 1)
            eta_str = time.strftime('%H:%M:%S', time.gmtime(eta))
        else:
            eta_str = "计算中..."
        
        elapsed_str = time.strftime('%H:%M:%S', time.gmtime(elapsed))
        
        print("\n" + "="*70)
        print(f"📄 [{i}/{len(md_files)}] {md_file}")
        print(f"⏱️  已用时: {elapsed_str} | 预计剩余: {eta_str}")
        print("="*70)
        
        try:
            # 处理文件
            result = process_single_file(md_path, model)
            
            # 生成输出文件名
            course_code = result.get('course_code', '未找到')
            course_name = result.get('course_name', '未找到')
            output_filename = f"{course_code}_{course_name}.json"
            output_path = os.path.join(output_dir, output_filename)
            
            # 检查是否跳过
            if skip_existing and os.path.exists(output_path):
                print(f"      ⏭️  跳过（已存在）: {output_filename}")
                skipped_count += 1
                continue
            
            # 保存结果
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print(f"      ✅ 成功保存: {output_filename}")
            success_count += 1
            
        except Exception as e:
            print(f"      ❌ 处理失败: {e}")
            failed_count += 1
    
    # 最终统计
    total_time = time.time() - start_time
    total_time_str = time.strftime('%H:%M:%S', time.gmtime(total_time))
    avg_time = total_time / len(md_files) if md_files else 0
    
    print("\n" + "="*70)
    print("🎉 处理完成!")
    print("="*70)
    print(f"  ✅ 成功: {success_count} 个文件")
    print(f"  ❌ 失败: {failed_count} 个文件")
    print(f"  ⏭️  跳过: {skipped_count} 个文件")
    print(f"  ⏱️  总耗时: {total_time_str}")
    print(f"  📊 平均速度: {avg_time:.2f}秒/文件")
    print(f"  📁 输出目录: {output_dir}")
    print("="*70)


if __name__ == '__main__':
    # 批量处理所有文件
    process_all_markdown_files(
        input_dir='docs/md',
        output_dir='docs/json',  # 使用新目录避免覆盖
        model='qwen2.5:7b',
        skip_existing=False
    )

