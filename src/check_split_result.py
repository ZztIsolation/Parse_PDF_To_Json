"""
检查PDF分割结果
显示统计信息和文件列表
"""

import os
from pypdf import PdfReader

def check_split_result(directory: str) -> None:
    """
    检查分割结果并显示统计信息
    
    参数:
        directory: PDF文件所在目录
    """
    if not os.path.exists(directory):
        print(f"❌ 错误: 目录不存在: {directory}")
        return
    
    # 获取所有PDF文件
    pdf_files = sorted([f for f in os.listdir(directory) if f.endswith('.pdf')])
    
    if not pdf_files:
        print(f"❌ 目录中没有PDF文件: {directory}")
        return
    
    print(f"\n{'='*60}")
    print("📊 PDF分割结果统计")
    print(f"{'='*60}\n")
    print(f"输出目录: {directory}")
    print(f"文件总数: {len(pdf_files)} 个\n")
    
    # 统计页数
    total_pages = 0
    page_counts = []
    
    print("正在统计页数...")
    for pdf_file in pdf_files:
        try:
            pdf_path = os.path.join(directory, pdf_file)
            reader = PdfReader(pdf_path)
            page_count = len(reader.pages)
            total_pages += page_count
            page_counts.append(page_count)
        except Exception as e:
            print(f"⚠️  警告: 无法读取 {pdf_file}: {e}")
            page_counts.append(0)
    
    # 显示统计信息
    print(f"\n{'='*60}")
    print("📈 页数统计:")
    print(f"{'='*60}")
    print(f"  总页数: {total_pages} 页")
    print(f"  平均页数: {total_pages / len(pdf_files):.1f} 页/文件")
    print(f"  最少页数: {min(page_counts)} 页")
    print(f"  最多页数: {max(page_counts)} 页")
    
    # 按页数分组统计
    print(f"\n{'='*60}")
    print("📊 页数分布:")
    print(f"{'='*60}")
    ranges = [
        (0, 5, "1-5页"),
        (5, 10, "6-10页"),
        (10, 15, "11-15页"),
        (15, 20, "16-20页"),
        (20, float('inf'), "20页以上")
    ]
    
    for min_pages, max_pages, label in ranges:
        count = sum(1 for p in page_counts if min_pages < p <= max_pages)
        if count > 0:
            percentage = count / len(pdf_files) * 100
            print(f"  {label}: {count} 个文件 ({percentage:.1f}%)")
    
    # 显示文件列表(前20个和后10个)
    print(f"\n{'='*60}")
    print("📋 文件列表 (前20个):")
    print(f"{'='*60}")
    for i, pdf_file in enumerate(pdf_files[:20]):
        pages = page_counts[i]
        print(f"  {pdf_file} ({pages}页)")
    
    if len(pdf_files) > 30:
        print(f"\n  ... 省略 {len(pdf_files) - 30} 个文件 ...\n")
        
        print(f"{'='*60}")
        print("📋 文件列表 (后10个):")
        print(f"{'='*60}")
        for i, pdf_file in enumerate(pdf_files[-10:]):
            idx = len(pdf_files) - 10 + i
            pages = page_counts[idx]
            print(f"  {pdf_file} ({pages}页)")
    
    # 检查是否有一级标题的文件
    print(f"\n{'='*60}")
    print("🔍 检查一级标题文件:")
    print(f"{'='*60}")
    
    level0_keywords = ['前言', '目录', '思政类', '数学类', '物理类', '英语类', '军体类', '工程基础类', '专业类']
    level0_files = []
    
    for pdf_file in pdf_files:
        if any(keyword in pdf_file for keyword in level0_keywords):
            level0_files.append(pdf_file)
    
    if level0_files:
        print(f"⚠️  发现 {len(level0_files)} 个可能的一级标题文件:")
        for f in level0_files:
            print(f"  - {f}")
    else:
        print("✅ 没有发现一级标题文件,所有文件都是具体课程!")
    
    print(f"\n{'='*60}")
    print("✅ 检查完成!")
    print(f"{'='*60}")
    print(f"\n💡 提示: 这些PDF文件都符合MinerU API的限制(每个文件≤20页)")
    print(f"   可以直接用于批量转换为Markdown格式\n")


def main():
    """主函数"""
    directory = "docs/all"
    
    print(f"\n{'#'*60}")
    print("# PDF分割结果检查")
    print(f"{'#'*60}\n")
    
    check_split_result(directory)
    
    print(f"{'#'*60}")
    print("# 检查完成")
    print(f"{'#'*60}\n")


if __name__ == "__main__":
    main()

