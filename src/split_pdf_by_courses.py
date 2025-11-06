"""
PDF分割工具 - 按具体课程分割(只保留前3页)
将PDF按二级书签(具体课程名称)分割成多个小PDF文件
每个课程只保留前3页(课程目标、毕业要求对应关系、教学内容概览)
"""

from pypdf import PdfReader, PdfWriter
import os
import re
from typing import List, Dict, Optional


def get_bookmarks_with_pages(pdf_path: str) -> Optional[List[Dict]]:
    """
    提取PDF的书签及其对应的页码
    
    参数:
        pdf_path: PDF文件路径
        
    返回:
        书签列表,格式: [{"title": "标题", "page": 页码, "level": 层级}, ...]
        如果没有书签则返回None
    """
    reader = PdfReader(pdf_path)
    bookmarks = []
    
    def extract_bookmarks(outline, level=0):
        """递归提取所有层级的书签"""
        for item in outline:
            if isinstance(item, list):
                # 处理嵌套书签
                extract_bookmarks(item, level + 1)
            else:
                # 获取书签标题
                title = item.title
                # 获取书签指向的页码
                try:
                    page_num = reader.get_destination_page_number(item)
                    bookmarks.append({
                        'title': title,
                        'page': page_num,
                        'level': level
                    })
                except Exception as e:
                    print(f"⚠️  警告: 无法获取书签 '{title}' 的页码: {e}")
    
    # 检查是否有书签
    if reader.outline:
        extract_bookmarks(reader.outline)
    else:
        print("❌ 警告: 该PDF没有书签/目录结构!")
        return None
    
    return bookmarks


def split_pdf_by_level1_bookmarks(pdf_path: str, output_dir: str) -> None:
    """
    根据二级书签(具体课程)分割PDF
    
    参数:
        pdf_path: 输入PDF路径
        output_dir: 输出目录
    """
    # 读取PDF
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    
    print(f"\n{'='*60}")
    print(f"📄 PDF信息:")
    print(f"{'='*60}")
    print(f"  文件路径: {pdf_path}")
    print(f"  总页数: {total_pages}")
    
    # 获取书签
    bookmarks = get_bookmarks_with_pages(pdf_path)
    
    if not bookmarks:
        print("\n❌ 无法分割: PDF没有书签")
        return
    
    # 筛选二级书签(level=1,即具体课程)
    level1_bookmarks = [b for b in bookmarks if b['level'] == 1]
    
    if not level1_bookmarks:
        print(f"\n❌ 错误: 没有找到二级书签(具体课程)")
        return
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n{'='*60}")
    print(f"📊 书签统计:")
    print(f"{'='*60}")
    print(f"  找到 {len(level1_bookmarks)} 个具体课程")
    print(f"  预计生成 {len(level1_bookmarks)} 个PDF文件")
    
    print(f"\n{'='*60}")
    print(f"✂️  开始分割 (按具体课程)")
    print(f"{'='*60}\n")
    
    # 为每个课程确定页码范围并分割
    success_count = 0
    skipped_count = 0
    
    for i, bookmark in enumerate(level1_bookmarks):
        start_page = bookmark['page']
        
        # 确定结束页码(下一个同级书签的起始页-1,或PDF末尾)
        if i < len(level1_bookmarks) - 1:
            end_page = level1_bookmarks[i + 1]['page'] - 1
        else:
            end_page = total_pages - 1
        
        page_count = end_page - start_page + 1
        
        # 跳过"目录"、"前言"等非课程内容
        title = bookmark['title']
        skip_keywords = ['目录', '目       录', '前言', '前    言', '前  言']
        if any(keyword in title for keyword in skip_keywords):
            print(f"⏭️  [{i+1}/{len(level1_bookmarks)}] 跳过: {title} (非课程内容)")
            skipped_count += 1
            continue
        
        # 清理文件名(移除非法字符)
        safe_title = re.sub(r'[\\/*?:"<>|《》]', '', bookmark['title'])
        safe_title = safe_title.strip()
        safe_title = safe_title.replace('课程教学大纲', '').strip()  # 简化文件名
        
        # 生成输出文件名
        output_filename = f"{i+1:03d}_{safe_title}.pdf"
        output_path = os.path.join(output_dir, output_filename)
        
        try:
            # 只保留前3页
            actual_end_page = min(start_page + 2, end_page)  # 前3页: start_page, start_page+1, start_page+2
            actual_page_count = actual_end_page - start_page + 1

            # 创建新PDF
            writer = PdfWriter()
            for page_num in range(start_page, actual_end_page + 1):
                writer.add_page(reader.pages[page_num])

            # 保存
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)

            print(f"✅ [{i+1}/{len(level1_bookmarks)}] {output_filename}")
            print(f"    页码: {start_page+1}-{actual_end_page+1} (共 {actual_page_count} 页, 原始 {page_count} 页)")
            success_count += 1
            
        except Exception as e:
            print(f"❌ [{i+1}/{len(level1_bookmarks)}] 失败: {bookmark['title']}")
            print(f"    错误: {e}")
    
    # 输出统计信息
    print(f"\n{'='*60}")
    print(f"🎉 分割完成!")
    print(f"{'='*60}")
    print(f"  成功: {success_count} 个文件")
    print(f"  跳过: {skipped_count} 个文件")
    print(f"  失败: {len(level1_bookmarks) - success_count - skipped_count} 个文件")
    print(f"  输出目录: {output_dir}")


def main():
    """主函数"""
    # 配置参数
    input_pdf = "docs/25. 计算机科学与技术专业.pdf"
    output_directory = "docs/all"
    
    print(f"\n{'#'*60}")
    print("# PDF分割工具 - 按具体课程分割")
    print(f"{'#'*60}\n")
    
    # 检查输入文件是否存在
    if not os.path.exists(input_pdf):
        print(f"❌ 错误: 找不到输入文件: {input_pdf}")
        return
    
    # 执行分割
    split_pdf_by_level1_bookmarks(input_pdf, output_directory)
    
    print(f"\n{'#'*60}")
    print("# 处理完成")
    print(f"{'#'*60}\n")


if __name__ == "__main__":
    main()

