"""
PDF转Markdown批量转换工具 - Unstructured版本
使用Unstructured库的fast策略将所有课程PDF转换为Markdown格式
"""

import os
from pathlib import Path
import time
from datetime import timedelta


def convert_pdf_to_markdown_unstructured(
    input_dir='docs/all',
    output_dir='docs/md_uns',
    overwrite=False,
    strategy='fast'
):
    """
    使用Unstructured库批量将PDF转换为Markdown
    
    参数:
        input_dir: 输入PDF目录
        output_dir: 输出Markdown目录
        overwrite: 是否覆盖已存在的文件
        strategy: unstructured的处理策略 ('fast', 'hi_res', 'auto')
    """
    
    try:
        from unstructured.partition.pdf import partition_pdf
        from unstructured.staging.base import elements_to_text
    except ImportError:
        print("❌ 未安装unstructured库")
        print("请运行: pip install unstructured[pdf]")
        print("或: pip install unstructured")
        return
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取所有PDF文件
    pdf_files = sorted([f for f in os.listdir(input_dir) if f.endswith('.pdf')])
    
    if not pdf_files:
        print(f"❌ 在 {input_dir} 中没有找到PDF文件")
        return
    
    print(f"\n{'='*70}")
    print(f"📄 PDF转Markdown批量转换 (Unstructured - {strategy})")
    print(f"{'='*70}")
    print(f"输入目录: {input_dir}")
    print(f"输出目录: {output_dir}")
    print(f"PDF总数: {len(pdf_files)}")
    print(f"覆盖模式: {'是' if overwrite else '否'}")
    print(f"处理策略: {strategy}")
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
            # 使用Unstructured转换
            file_start_time = time.time()
            
            # 分区PDF文档
            elements = partition_pdf(
                filename=pdf_path,
                strategy=strategy,
                infer_table_structure=True,  # 推断表格结构
                include_page_breaks=False,   # 不包含分页符
            )
            
            # 转换为Markdown格式
            markdown_lines = []
            prev_type = None

            for element in elements:
                element_type = type(element).__name__
                text = element.text.strip()

                if not text:
                    continue

                # 根据元素类型添加Markdown格式
                if element_type == 'Title':
                    # 标题前后添加空行
                    if prev_type and prev_type != 'Title':
                        markdown_lines.append('')
                    markdown_lines.append(f"## {text}")
                    markdown_lines.append('')
                elif element_type == 'NarrativeText':
                    # 普通文本
                    markdown_lines.append(text)
                elif element_type == 'ListItem':
                    # 列表项
                    markdown_lines.append(f"- {text}")
                elif element_type == 'Table':
                    # 表格前后添加空行
                    if prev_type:
                        markdown_lines.append('')
                    markdown_lines.append(text)
                    markdown_lines.append('')
                else:
                    # 其他类型（如PageBreak等）
                    markdown_lines.append(text)

                prev_type = element_type

            markdown_text = '\n'.join(markdown_lines)
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
            print(f"   元素数: {len(elements)} | 行数: {lines:,} | 字符数: {chars:,}")
            print(f"   耗时: {file_elapsed_time:.2f}秒")
            success_count += 1

        except Exception as e:
            print(f"❌ 转换失败: {e}")
            failed_count += 1
    
    # 计算总时间
    total_time = time.time() - start_time
    total_time_str = str(timedelta(seconds=int(total_time)))

    # 打印总结
    print(f"\n{'='*70}")
    print(f"📊 转换完成统计")
    print(f"{'='*70}")
    print(f"✅ 成功: {success_count}")
    print(f"❌ 失败: {failed_count}")
    print(f"⏭️  跳过: {skipped_count}")
    print(f"📝 总行数: {total_lines:,}")
    print(f"📝 总字符数: {total_chars:,}")
    print(f"⏱️  总耗时: {total_time_str}")
    if success_count > 0:
        avg_time = total_time / success_count
        print(f"⏱️  平均耗时: {avg_time:.2f}秒/文件")
    print(f"{'='*70}\n")


if __name__ == '__main__':
    # 测试转换前5个文件
    import sys
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == '--all':
            # 转换所有文件
            convert_pdf_to_markdown_unstructured(
                input_dir='docs/all',
                output_dir='docs/md_uns',
                overwrite=False,
                strategy='hi_res'
            )
        elif sys.argv[1] == '--test':
            # 测试模式：只转换前5个文件
            print("🧪 测试模式：只转换前5个文件\n")
            
            # 临时修改函数以只处理前5个文件
            input_dir = 'docs/all'
            output_dir = 'docs/md_uns'
            
            os.makedirs(output_dir, exist_ok=True)
            pdf_files = sorted([f for f in os.listdir(input_dir) if f.endswith('.pdf')])[:5]
            
            print(f"测试文件列表:")
            for i, f in enumerate(pdf_files, 1):
                print(f"  {i}. {f}")
            print()
            
            # 创建临时目录并复制文件
            test_dir = 'docs/all_test'
            os.makedirs(test_dir, exist_ok=True)
            
            import shutil
            for pdf_file in pdf_files:
                src = os.path.join(input_dir, pdf_file)
                dst = os.path.join(test_dir, pdf_file)
                if not os.path.exists(dst):
                    shutil.copy2(src, dst)
            
            # 转换测试文件
            # 注意：hi_res需要安装poppler，如果没有安装会失败
            # 可以使用 'fast' 或 'auto' 策略
            convert_pdf_to_markdown_unstructured(
                input_dir=test_dir,
                output_dir=output_dir,
                overwrite=True,
                strategy='auto'
            )
        else:
            print("用法:")
            print("  python src/pdf_to_markdown_unstructured.py --test   # 测试模式（前5个文件）")
            print("  python src/pdf_to_markdown_unstructured.py --all    # 转换所有文件")
    else:
        print("用法:")
        print("  python src/pdf_to_markdown_unstructured.py --test   # 测试模式（前5个文件）")
        print("  python src/pdf_to_markdown_unstructured.py --all    # 转换所有文件")

