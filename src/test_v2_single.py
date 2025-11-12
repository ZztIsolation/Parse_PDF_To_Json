"""
测试V2版本 - 单个文件测试

测试AI提取课程名称和代码的准确性
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from process_markdown import process_single_file
import json

# 测试几个不同格式的文件
test_files = [
    'docs/md/002_中国近现代史纲要.md',  # 一级标题
    'docs/md/003_毛泽东思想和中国特色社会主义理论体系概论.md',  # 一级标题
    'docs/md/017_线性代数.md',  # 二级标题
    'docs/md/026_大学物理实验B.md',  # 一级标题，课程代码不同
    'docs/md/061_程序设计基础.md',  # 复杂文件
]

print("="*70)
print("测试V2版本 - AI提取课程名称和代码")
print("="*70)

for test_file in test_files:
    if not os.path.exists(test_file):
        print(f"\n❌ 文件不存在: {test_file}")
        continue
    
    print(f"\n{'='*70}")
    print(f"📄 测试文件: {os.path.basename(test_file)}")
    print(f"{'='*70}")
    
    try:
        result = process_single_file(test_file, model='qwen2.5:7b')
        
        print(f"\n提取结果:")
        print(f"  课程名称: {result.get('course_name', '未找到')}")
        print(f"  课程代码: {result.get('course_code', '未找到')}")
        print(f"  课程目标: {len(result.get('course_goals', ''))} 字符")
        print(f"  对应关系表格: {len(result.get('requirement_mappings', []))} 个")
        
        # 保存结果
        output_file = f"test_v2_{os.path.basename(test_file).replace('.md', '.json')}"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 已保存: {output_file}")
        
    except Exception as e:
        print(f"\n❌ 处理失败: {e}")
        import traceback
        traceback.print_exc()

print(f"\n{'='*70}")
print("测试完成！")
print(f"{'='*70}")

