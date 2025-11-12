"""
PDF转Markdown批量转换工具
使用PyMuPDF4LLM将所有课程PDF转换为Markdown格式
"""

import os
import pymupdf4llm
from pathlib import Path
import time
from datetime import timedelta


def convert_pdf_to_markdown(
    input_dir='docs/all',
    output_dir='docs/md',
    overwrite=False
):
    """
    批量将PDF转换为Markdown
    
    参数:
        input_dir: 输入PDF目录
        output_dir: 输出Markdown目录
        overwrite: 是否覆盖已存在的文件
    """
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取所有PDF文件
    pdf_files = sorted([f for f in os.listdir(input_dir) if f.endswith('.pdf')])
    
    if not pdf_files:
        print(f"❌ 在 {input_dir} 中没有找到PDF文件")
        return
    
    print(f"\n{'='*70}")
    print(f"📄 PDF转Markdown批量转换")
    print(f"{'='*70}")
    print(f"输入目录: {input_dir}")
    print(f"输出目录: {output_dir}")
    print(f"PDF总数: {len(pdf_files)}")
    print(f"覆盖模式: {'是' if overwrite else '否'}")
    print(f"{'='*70}\n")

    # 统计信息
    success_count = 0
    failed_count = 0
    skipped_count = 0
    total_lines = 0
    total_chars = 0

    # 开始计时
    start_time = time.time()

    # 转换每个文件
    for i, pdf_file in enumerate(pdf_files, 1):
        # 计算进度
        progress = i / len(pdf_files) * 100
        elapsed_time = time.time() - start_time

        # 估算剩余时间
        if i > 1:
            avg_time_per_file = elapsed_time / (i - 1)
            remaining_files = len(pdf_files) - i + 1
            estimated_remaining = avg_time_per_file * remaining_files
            eta_str = str(timedelta(seconds=int(estimated_remaining)))
        else:
            eta_str = "计算中..."
        pdf_path = os.path.join(input_dir, pdf_file)
        md_filename = pdf_file.replace('.pdf', '.md')
        md_path = os.path.join(output_dir, md_filename)

        # 显示进度条和当前处理文件
        elapsed_str = str(timedelta(seconds=int(elapsed_time)))
        bar_length = 40
        filled_length = int(bar_length * i // len(pdf_files))
        bar = '█' * filled_length + '░' * (bar_length - filled_length)

        print(f"\n{'='*70}")
        print(f"📊 进度: [{bar}] {progress:.1f}% ({i}/{len(pdf_files)})")
        print(f"⏱️  已用时间: {elapsed_str} | 预计剩余: {eta_str}")
        print(f"📄 正在处理: {pdf_file}")
        print(f"{'='*70}")

        # 检查是否已存在
        if os.path.exists(md_path) and not overwrite:
            print(f"⏭️  跳过 (已存在)")
            skipped_count += 1
            continue

        try:
            # 使用PyMuPDF4LLM转换
            file_start_time = time.time()
            markdown_text = pymupdf4llm.to_markdown(pdf_path)
            file_elapsed_time = time.time() - file_start_time

            # 保存Markdown文件
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(markdown_text)

            # 统计信息
            lines = markdown_text.count('\n')
            chars = len(markdown_text)
            total_lines += lines
            total_chars += chars

            print(f"✅ 转换成功!")
            print(f"   输出: {md_filename}")
            print(f"   行数: {lines:,} | 字符数: {chars:,}")
            print(f"   耗时: {file_elapsed_time:.2f}秒")
            success_count += 1

        except Exception as e:
            print(f"❌ 转换失败: {e}")
            failed_count += 1
    
    # 计算总时间
    total_time = time.time() - start_time
    total_time_str = str(timedelta(seconds=int(total_time)))
    avg_time_per_file = total_time / len(pdf_files) if len(pdf_files) > 0 else 0

    # 总结
    print(f"\n{'='*70}")
    print(f"🎉 转换完成!")
    print(f"{'='*70}")
    print(f"  成功: {success_count} 个文件")
    print(f"  失败: {failed_count} 个文件")
    print(f"  跳过: {skipped_count} 个文件")
    print(f"  总行数: {total_lines:,} 行")
    print(f"  总字符数: {total_chars:,} 字符")
    print(f"  总耗时: {total_time_str} ({total_time:.2f}秒)")
    print(f"  平均速度: {avg_time_per_file:.2f}秒/文件")
    print(f"  输出目录: {output_dir}")
    print(f"{'='*70}\n")
    
    if success_count > 0:
        print(f"💡 提示: 请检查生成的Markdown文件质量")
        print(f"   可以打开几个文件查看:")
        print(f"   - 标题层级是否正确?")
        print(f"   - 表格格式是否完整?")
        print(f"   - 列表格式是否正确?")
        print(f"{'='*70}\n")


def convert_single_pdf(pdf_path, output_path=None):
    """
    转换单个PDF文件
    
    参数:
        pdf_path: PDF文件路径
        output_path: 输出Markdown文件路径(可选,默认为同名.md文件)
    """
    if not os.path.exists(pdf_path):
        print(f"❌ 文件不存在: {pdf_path}")
        return False
    
    # 确定输出路径
    if output_path is None:
        output_path = pdf_path.replace('.pdf', '.md')
    
    print(f"转换: {pdf_path}")
    print(f"输出: {output_path}")
    
    try:
        # 转换
        markdown_text = pymupdf4llm.to_markdown(pdf_path)
        
        # 保存
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_text)
        
        lines = markdown_text.count('\n')
        chars = len(markdown_text)
        
        print(f"✅ 转换成功!")
        print(f"   行数: {lines}")
        print(f"   字符数: {chars}")
        
        return True
        
    except Exception as e:
        print(f"❌ 转换失败: {e}")
        return False


if __name__ == "__main__":
    # 批量转换所有PDF
    convert_pdf_to_markdown(
        input_dir='docs/all',
        output_dir='docs/md',
        overwrite=False  # 设置为True可以覆盖已存在的文件
    )
    
    # 单个文件转换示例:
    # convert_single_pdf('docs/all/064_数据结构.pdf', 'docs/md/064_数据结构.md')

