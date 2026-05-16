#!/usr/bin/env python3
"""
Markdown to PDF Converter
用于将软件著作权申请材料从Markdown格式转换为PDF格式
"""

import os
import sys
import subprocess
from pathlib import Path


def check_dependencies():
    """检查依赖是否已安装"""
    print("正在检查依赖...")
    
    try:
        import markdown
        print("✓ markdown 已安装")
    except ImportError:
        print("✗ markdown 未安装")
        print("请运行：pip install markdown")
        return False
    
    try:
        import pdfkit
        print("✓ pdfkit 已安装")
    except ImportError:
        print("✗ pdfkit 未安装")
        print("请运行：pip install pdfkit")
        return False
    
    try:
        subprocess.run(['wkhtmltopdf', '--version'], 
                      capture_output=True, 
                      check=True)
        print("✓ wkhtmltopdf 已安装")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ wkhtmltopdf 未安装")
        print("请运行：")
        print("  Ubuntu/Debian: sudo apt-get install wkhtmltopdf")
        print("  macOS: brew install wkhtmltopdf")
        print("  Windows: 从 https://wkhtmltopdf.org/downloads.html 下载安装")
        return False
    
    return True


def markdown_to_html(markdown_file, output_html):
    """将Markdown转换为HTML"""
    import markdown
    
    with open(markdown_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    html_template = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{Path(markdown_file).stem}</title>
    <style>
        body {{
            font-family: "Microsoft YaHei", "SimHei", "Arial", sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
            color: #333;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            font-size: 2em;
        }}
        h2 {{
            color: #34495e;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 8px;
            margin-top: 30px;
            font-size: 1.5em;
        }}
        h3 {{
            color: #7f8c8d;
            font-size: 1.2em;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #3498db;
            color: white;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: "Courier New", Courier, monospace;
        }}
        pre {{
            background-color: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            border-left: 4px solid #3498db;
        }}
        hr {{
            border: none;
            border-top: 2px solid #ecf0f1;
            margin: 30px 0;
        }}
        ul, ol {{
            padding-left: 30px;
        }}
        li {{
            margin: 8px 0;
        }}
        strong {{
            color: #e74c3c;
        }}
        p {{
            margin: 15px 0;
            text-align: justify;
        }}
        @media print {{
            body {{
                margin: 0;
                padding: 20px;
            }}
            h1 {{
                page-break-before: always;
            }}
        }}
    </style>
</head>
<body>
{markdown.markdown(md_content, extensions=['tables', 'fenced_code'])}
</body>
</html>'''
    
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    return True


def html_to_pdf(html_file, output_pdf):
    """将HTML转换为PDF"""
    import pdfkit
    
    try:
        pdfkit.from_file(html_file, output_pdf, options={
            'page-size': 'A4',
            'margin-top': '20mm',
            'margin-right': '20mm',
            'margin-bottom': '20mm',
            'margin-left': '20mm',
            'encoding': 'UTF-8',
            'no-outline': None,
            'enable-local-file-access': None
        })
        return True
    except Exception as e:
        print(f"转换PDF失败：{e}")
        return False


def convert_markdown_to_pdf(markdown_file, output_pdf=None):
    """将Markdown文件转换为PDF"""
    if output_pdf is None:
        output_pdf = Path(markdown_file).with_suffix('.pdf')
    
    temp_html = Path(markdown_file).with_suffix('.html')
    
    print(f"正在转换：{markdown_file}")
    
    if not markdown_to_html(markdown_file, temp_html):
        return False
    
    if html_to_pdf(temp_html, output_pdf):
        print(f"✓ 已生成：{output_pdf}")
        temp_html.unlink()
        return True
    else:
        return False


def convert_directory(input_dir, output_dir=None):
    """转换目录中的所有Markdown文件"""
    input_path = Path(input_dir)
    
    if output_dir is None:
        output_dir = input_path
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    
    md_files = list(input_path.glob('*.md'))
    
    if not md_files:
        print("未找到Markdown文件")
        return
    
    print(f"找到 {len(md_files)} 个Markdown文件")
    print(f"输出目录：{output_dir}\n")
    
    success_count = 0
    for md_file in md_files:
        output_pdf = output_dir / f"{md_file.stem}.pdf"
        if convert_markdown_to_pdf(md_file, output_pdf):
            success_count += 1
    
    print(f"\n转换完成：{success_count}/{len(md_files)} 个文件成功转换")


def main():
    if len(sys.argv) < 2:
        print("Markdown to PDF Converter")
        print("用于将软件著作权申请材料从Markdown格式转换为PDF格式\n")
        print("使用方法：")
        print("  python convert_to_pdf.py <markdown_file> [output_pdf]")
        print("  python convert_to_pdf.py <directory> [output_directory]")
        print("\n示例：")
        print("  python convert_to_pdf.py 源代码文档.md")
        print("  python convert_to_pdf.py copyright-application-materials/")
        sys.exit(1)
    
    if not check_dependencies():
        sys.exit(1)
    
    input_path = sys.argv[1]
    
    if len(sys.argv) > 2:
        output_path = sys.argv[2]
    else:
        output_path = None
    
    if os.path.isfile(input_path):
        if output_path:
            convert_markdown_to_pdf(input_path, output_path)
        else:
            convert_markdown_to_pdf(input_path)
    elif os.path.isdir(input_path):
        convert_directory(input_path, output_path)
    else:
        print(f"错误：{input_path} 不存在")
        sys.exit(1)


if __name__ == '__main__':
    main()
