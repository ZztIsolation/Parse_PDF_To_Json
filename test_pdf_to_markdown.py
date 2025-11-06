"""
测试PDF转Markdown转换
使用PyMuPDF4LLM随机挑选几个PDF进行转换测试
"""

import os
import random
import pymupdf4llm
from pathlib import Path


def test_pdf_to_markdown(
    input_dir='docs/all',
    output_dir='docs/md',
    num_samples=5,
    specific_files=None
):
    """
    测试PDF转Markdown转换
    
    参数:
        input_dir: 输入PDF目录
        output_dir: 输出Markdown目录
        num_samples: 随机抽取的文件数量
        specific_files: 指定要转换的文件列表(如果提供,则忽略num_samples)
    """
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取所有PDF文件
    pdf_files = sorted([f for f in os.listdir(input_dir) if f.endswith('.pdf')])
    
    if not pdf_files:
        print(f"❌ 在 {input_dir} 中没有找到PDF文件")
        return
    
    print(f"\n{'='*60}")
    print(f"📄 PDF转Markdown测试")
    print(f"{'='*60}")
    print(f"输入目录: {input_dir}")
    print(f"输出目录: {output_dir}")
    print(f"PDF总数: {len(pdf_files)}")
    
    # 选择要转换的文件
    if specific_files:
        selected_files = [f for f in specific_files if f in pdf_files]
        if not selected_files:
            print(f"❌ 指定的文件不存在")
            return
        print(f"转换模式: 指定文件")
    else:
        # 随机选择,确保包含不同类型的课程
        selected_files = random.sample(pdf_files, min(num_samples, len(pdf_files)))
        print(f"转换模式: 随机抽样 ({num_samples}个)")
    
    print(f"\n{'='*60}")
    print(f"📋 选中的文件:")
    print(f"{'='*60}")
    for i, f in enumerate(selected_files, 1):
        print(f"  {i}. {f}")
    
    # 转换每个文件
    print(f"\n{'='*60}")
    print(f"🔄 开始转换...")
    print(f"{'='*60}\n")
    
    success_count = 0
    failed_count = 0
    
    for i, pdf_file in enumerate(selected_files, 1):
        pdf_path = os.path.join(input_dir, pdf_file)
        md_filename = pdf_file.replace('.pdf', '.md')
        md_path = os.path.join(output_dir, md_filename)
        
        print(f"[{i}/{len(selected_files)}] 转换: {pdf_file}")
        
        try:
            # 使用PyMuPDF4LLM转换
            markdown_text = pymupdf4llm.to_markdown(pdf_path)
            
            # 保存Markdown文件
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(markdown_text)
            
            # 统计信息
            lines = markdown_text.count('\n')
            chars = len(markdown_text)
            
            print(f"  ✅ 成功")
            print(f"     输出: {md_filename}")
            print(f"     行数: {lines}")
            print(f"     字符数: {chars}")
            
            success_count += 1
            
        except Exception as e:
            print(f"  ❌ 失败: {e}")
            failed_count += 1
        
        print()
    
    # 总结
    print(f"{'='*60}")
    print(f"🎉 转换完成!")
    print(f"{'='*60}")
    print(f"  成功: {success_count} 个文件")
    print(f"  失败: {failed_count} 个文件")
    print(f"  输出目录: {output_dir}")
    print(f"\n💡 提示: 请检查生成的Markdown文件质量:")
    print(f"  - 标题层级是否正确?")
    print(f"  - 表格格式是否完整?")
    print(f"  - 列表格式是否正确?")
    print(f"{'='*60}\n")


def test_with_representative_samples():
    """
    测试代表性样本:包含不同类型的课程
    """
    representative_files = [
        '002_中国近现代史纲要.pdf',           # 思政类
        '017_线性代数.pdf',                    # 数学类
        '064_数据结构.pdf',                    # 专业核心课
        '066_操作系统.pdf',                    # 专业核心课
        '079_机器学习.pdf',                    # AI课程
    ]
    
    print("\n" + "="*60)
    print("🎯 测试模式: 代表性样本")
    print("="*60)
    print("包含不同类型的课程,以全面评估转换质量\n")
    
    test_pdf_to_markdown(
        input_dir='docs/all',
        output_dir='docs/md',
        specific_files=representative_files
    )


if __name__ == "__main__":
    # 方式1: 测试代表性样本(推荐)
    test_with_representative_samples()
    
    # 方式2: 随机测试5个文件
    # test_pdf_to_markdown(num_samples=5)
    
    # 方式3: 指定特定文件
    # test_pdf_to_markdown(specific_files=['064_数据结构.pdf', '079_机器学习.pdf'])

