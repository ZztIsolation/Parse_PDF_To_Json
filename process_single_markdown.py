#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单个Markdown文件处理工具
用于测试和调试单个课程的Markdown转JSON

使用方法：
1. 修改下面的 TARGET_FILE 变量，指定要处理的Markdown文件名
2. 运行脚本：python process_single_markdown.py
3. 查看输出的JSON文件和详细报告
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from process_markdown import process_single_file
import json

# ============================================================
# 配置区域 - 在这里修改要处理的文件
# ============================================================

# 方式1：直接指定文件名（推荐）
TARGET_FILE = "061_程序设计基础.md"

# 方式2：从列表中选择（取消注释使用）
# 常见的课程文件示例：
# TARGET_FILE = "008_形势与政策4.md"
# TARGET_FILE = "025_物理学原理及工程应用2.md"
# TARGET_FILE = "061_程序设计基础.md"
# TARGET_FILE = "064_数据结构.md"
# TARGET_FILE = "066_操作系统.md"
# TARGET_FILE = "067_工程伦理.md"

# 方式3：使用AI模型（可选）
# 默认使用 qwen2.5:7b，如果你换了模型，可以在这里修改
AI_MODEL = "qwen2.5:7b"

# ============================================================
# 配置结束
# ============================================================

def print_separator(char="=", length=70):
    """打印分隔线"""
    print(char * length)

def print_section(title):
    """打印章节标题"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def process_and_display(md_file_name, model='qwen2.5:7b'):
    """
    处理单个Markdown文件并显示详细信息

    Args:
        md_file_name: Markdown文件名（如 "061_程序设计基础.md"）
        model: 使用的AI模型
    """
    # 构建完整路径
    md_path = os.path.join("docs", "md", md_file_name)

    # 检查文件是否存在
    if not os.path.exists(md_path):
        print(f"❌ 错误：文件不存在: {md_path}")
        print("\n可用的文件列表：")
        md_dir = os.path.join("docs", "md")
        if os.path.exists(md_dir):
            files = sorted([f for f in os.listdir(md_dir) if f.endswith('.md')])
            for i, f in enumerate(files[:20], 1):  # 只显示前20个
                print(f"  {i:3d}. {f}")
            if len(files) > 20:
                print(f"  ... 还有 {len(files) - 20} 个文件")
        return None

    print_section(f"处理文件: {md_file_name}")
    print(f"文件路径: {md_path}")
    print(f"使用模型: {model}")

    # 调用主处理函数
    print("\n开始处理...\n")
    try:
        result = process_single_file(md_path, model)
    except Exception as e:
        print(f"\n❌ 处理失败: {e}")
        import traceback
        traceback.print_exc()
        return None

    # ============================================================
    # 显示详细结果
    # ============================================================
    print_section("处理结果详情")

    # 基本信息
    print(f"📄 课程名称: {result.get('course_name', '未知')}")
    print(f"📄 课程代码: {result.get('course_code', '未知')}")

    # 课程目标
    print(f"\n📚 课程目标:")
    course_goals = result.get('course_goals', {})
    if isinstance(course_goals, dict):
        print(f"   总述: {course_goals.get('overview', '')[:100]}...")
        goals = course_goals.get('goals', [])
        print(f"   具体目标数量: {len(goals)}")
        for goal in goals[:3]:  # 只显示前3个
            print(f"   - 目标{goal.get('number', '?')}: {goal.get('content', '')[:80]}...")
        if len(goals) > 3:
            print(f"   ... 还有 {len(goals) - 3} 个目标")
    else:
        print(f"   {course_goals}")

    # 毕业要求对应关系
    print(f"\n📊 毕业要求对应关系:")
    mappings = result.get('requirement_mappings', [])
    print(f"   表格数量: {len(mappings)}")

    if mappings:
        success_count = sum(1 for m in mappings if not m.get('error'))
        failed_count = len(mappings) - success_count
        print(f"   ✅ 成功: {success_count}")
        print(f"   ❌ 失败: {failed_count}")
        if len(mappings) > 0:
            print(f"   📈 成功率: {success_count/len(mappings)*100:.1f}%")

        # 显示每个表格的详情
        for i, mapping in enumerate(mappings, 1):
            print(f"\n   --- 表格 {i} ---")
            if mapping.get('error'):
                print(f"   ❌ 解析失败")
                print(f"   标题: {mapping.get('table_title', '未知')}")
                print(f"   专业: {mapping.get('major', '未知')}")
                print(f"   错误: {mapping.get('error', '')[:100]}")
            else:
                print(f"   ✅ 解析成功")
                print(f"   标题: {mapping.get('table_title', '未知')}")
                print(f"   专业: {mapping.get('major', '未知')}")
                print(f"   映射数量: {len(mapping.get('mappings', []))}")

                # 显示第一个映射
                if mapping.get('mappings'):
                    first = mapping['mappings'][0]
                    print(f"   第一个映射示例:")
                    print(f"     - 毕业要求{first.get('requirement_number', '?')}: {first.get('requirement', '')[:60]}...")
                    print(f"     - 指标点: {first.get('indicator', '')[:60]}...")
                    print(f"     - 课程目标: {first.get('course_goals', '')}")

    # 课程联系
    print(f"\n🔗 课程联系:")
    relations = result.get('course_relations', {})
    pre_courses = relations.get('prerequisite_courses', [])
    post_courses = relations.get('subsequent_courses', [])
    description = relations.get('description', '')

    print(f"   先修课程 ({len(pre_courses)}): {pre_courses}")
    print(f"   后续课程 ({len(post_courses)}): {post_courses}")
    if description:
        print(f"   描述: {description[:100]}...")

    # ============================================================
    # 保存结果
    # ============================================================
    print_section("保存结果")

    # 生成输出文件名
    base_name = os.path.splitext(md_file_name)[0]
    output_file = f"test_output_{base_name}.json"

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"✅ 结果已保存到: {output_file}")
        print(f"   文件大小: {os.path.getsize(output_file)} 字节")
    except Exception as e:
        print(f"❌ 保存失败: {e}")

    print_separator()
    print(f"✅ 全部完成！输出文件: {output_file}")
    print_separator()

    return result

# ============================================================
# 主程序
# ============================================================
if __name__ == "__main__":
    print_separator("=")
    print("  单个Markdown文件处理工具")
    print_separator("=")
    print(f"\n目标文件: {TARGET_FILE}")
    print(f"AI模型: {AI_MODEL}\n")

    # 处理文件
    result = process_and_display(TARGET_FILE, AI_MODEL)

    if result:
        print("\n✅ 全部完成！")
    else:
        print("\n❌ 处理失败")

