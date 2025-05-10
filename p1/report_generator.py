#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
词法分析结果PDF报告生成器
将词法分析结果输出为美观的PDF文档
"""

import os
import sys
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from lexical_analyzer import LexicalAnalyzer, identifiers, constants

# 注册中文字体（如果需要显示中文）
try:
    # 尝试注册系统中可能存在的中文字体
    pdfmetrics.registerFont(TTFont('SimSun', '/System/Library/Fonts/PingFang.ttc'))
    chinese_font = 'SimSun'
except:
    try:
        # 尝试其他可能的字体路径
        pdfmetrics.registerFont(TTFont('SimSun', '/Library/Fonts/Arial Unicode.ttf'))
        chinese_font = 'SimSun'
    except:
        try:
            # 尝试更多可能的字体路径
            pdfmetrics.registerFont(TTFont('SimSun', '/System/Library/Fonts/STHeiti Light.ttc'))
            chinese_font = 'SimSun'
        except:
            # 如果找不到中文字体，使用默认字体
            chinese_font = 'Helvetica'
            print("警告: 未找到中文字体，PDF中的中文可能无法正确显示")

class PdfReportGenerator:
    def __init__(self, output_path="词法分析报告.pdf"):
        self.output_path = output_path
        self.doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        self.styles = getSampleStyleSheet()
        self.init_styles()
        self.elements = []
        
    def init_styles(self):
        """初始化自定义样式"""
        # 添加自定义样式
        self.styles.add(ParagraphStyle(
            name='ChineseTitle',
            parent=self.styles['Title'],
            fontName=chinese_font,
            fontSize=20,
            alignment=TA_CENTER,
            spaceAfter=12
        ))
        
        self.styles.add(ParagraphStyle(
            name='ChineseHeading1',
            parent=self.styles['Heading1'],
            fontName=chinese_font,
            fontSize=16,
            alignment=TA_LEFT,
            spaceAfter=8
        ))
        
        self.styles.add(ParagraphStyle(
            name='ChineseHeading2',
            parent=self.styles['Heading2'],
            fontName=chinese_font,
            fontSize=14,
            alignment=TA_LEFT,
            spaceAfter=6
        ))
        
        self.styles.add(ParagraphStyle(
            name='ChineseNormal',
            parent=self.styles['Normal'],
            fontName=chinese_font,
            fontSize=12,
            alignment=TA_LEFT,
            spaceAfter=6
        ))
        
        self.styles.add(ParagraphStyle(
            name='ChineseCode',
            parent=self.styles['Code'],
            fontName='Courier',
            fontSize=10,
            alignment=TA_LEFT,
            spaceAfter=6
        ))

    def add_title(self, title):
        """添加标题"""
        self.elements.append(Paragraph(title, self.styles['ChineseTitle']))
        self.elements.append(Spacer(1, 12))
        
    def add_heading(self, text, level=1):
        """添加标题"""
        if level == 1:
            self.elements.append(Paragraph(text, self.styles['ChineseHeading1']))
        else:
            self.elements.append(Paragraph(text, self.styles['ChineseHeading2']))
        self.elements.append(Spacer(1, 6))
        
    def add_paragraph(self, text):
        """添加段落"""
        self.elements.append(Paragraph(text, self.styles['ChineseNormal']))
        self.elements.append(Spacer(1, 6))
        
    def add_code(self, text):
        """添加代码文本"""
        # 替换尖括号，避免被解释为HTML标签
        text = text.replace('<', '&lt;').replace('>', '&gt;')
        # 使用<pre>标签保留格式，但这可能在某些情况下不起作用
        # 考虑按行分割并添加每一行
        lines = text.split('\n')
        for line in lines:
            if line.strip():  # 如果行不为空
                self.elements.append(Paragraph(line, self.styles['ChineseCode']))
        self.elements.append(Spacer(1, 6))
        
    def add_table(self, data, colWidths=None, rowHeights=None, style=None):
        """添加表格"""
        if style is None:
            style = [
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), chinese_font),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), chinese_font),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]
            
        table = Table(data, colWidths=colWidths, rowHeights=rowHeights)
        table.setStyle(TableStyle(style))
        self.elements.append(table)
        self.elements.append(Spacer(1, 12))
        
    def add_spacer(self, height=12):
        """添加空白"""
        self.elements.append(Spacer(1, height))
        
    def add_page_break(self):
        """添加分页"""
        self.elements.append(PageBreak())
        
    def build(self):
        """生成PDF文档"""
        try:
            self.doc.build(self.elements)
            print(f"PDF报告已生成: {self.output_path}")
        except Exception as e:
            print(f"生成PDF报告时出错: {e}")

def generate_token_report(analyzer, file_path=None, description=None, report_generator=None):
    """将词法分析结果转换为PDF报告的一部分"""
    if report_generator is None:
        report_generator = PdfReportGenerator()
        
    # 添加分析文件信息
    if file_path:
        report_generator.add_heading(f"文件分析: {os.path.basename(file_path)}", 1)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            report_generator.add_heading("源代码", 2)
            report_generator.add_code(content)
        except Exception as e:
            report_generator.add_paragraph(f"无法读取源文件: {e}")
    elif description:
        report_generator.add_heading(f"代码分析: {description}", 1)
        try:
            report_generator.add_heading("源代码", 2)
            report_generator.add_code("""If i=0 then n++;
a<= 3b %);""")
        except Exception as e:
            report_generator.add_paragraph(f"无法显示源代码: {e}")
        
    # 添加分析结果表格
    report_generator.add_heading("词法分析结果", 2)
    
    # 表头
    table_data = [["单词", "二元序列", "类型", "位置（行，列）"]]
    
    # 表格内容
    for token in analyzer.tokens:
        if token['type'] == 'Error':
            type_name = "Error"
            attribute = "Error"
            row = [token['value'], f"({type_name},{attribute})", type_name, f"({token['line']}, {token['column']})"]
        else:
            type_name = analyzer.get_type_name(token['type'])
            attribute = token['value']
            row = [token['value'], f"({token['type']},{attribute})", type_name, f"({token['line']}, {token['column']})"]
        table_data.append(row)
    
    # 设置列宽
    col_widths = [120, 120, 100, 100]
    report_generator.add_table(table_data, colWidths=col_widths)
    
    # 添加统计信息
    report_generator.add_heading("分析统计", 2)
    report_generator.add_paragraph(f"标识符表: {identifiers}")
    report_generator.add_paragraph(f"常数表: {constants}")
    report_generator.add_paragraph(f"错误数量: {analyzer.error_count}")
    
    return report_generator

def generate_report_from_file(file_path, output_path=None):
    """从源文件生成PDF报告"""
    if not output_path:
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        output_path = f"{base_name}_分析报告.pdf"
        
    report_generator = PdfReportGenerator(output_path)
    
    # 添加报告标题和生成时间
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_generator.add_title("词法分析报告")
    report_generator.add_paragraph("李健豪 222241807417 计科2班")
    report_generator.add_paragraph(f"生成时间: {now}")
    
    # 分析文件
    analyzer = LexicalAnalyzer()
    if analyzer.load_file(file_path):
        analyzer.analyze()
        generate_token_report(analyzer, file_path, None, report_generator)
        
    # 生成PDF
    report_generator.build()
    
    return output_path

def generate_report_from_examples():
    """生成包含多个示例的综合报告"""
    # 清空标识符和常数表
    identifiers.clear()
    constants.clear()
    
    report_generator = PdfReportGenerator("词法分析综合报告.pdf")
    
    # 添加报告标题和生成时间
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_generator.add_title("词法分析综合报告")
    report_generator.add_paragraph("李健豪 222241807417 计科2班")
    report_generator.add_paragraph(f"生成时间: {now}")
    
    # 分析简单测试文件
    analyzer = LexicalAnalyzer()
    if analyzer.load_file("test.c"):
        analyzer.analyze()
        generate_token_report(analyzer, "test.c", None, report_generator)
        
    # 添加分页
    report_generator.add_page_break()
    
    # 分析复杂测试文件
    identifiers.clear()
    constants.clear()
    analyzer = LexicalAnalyzer()
    if analyzer.load_file("test_complex.c"):
        analyzer.analyze()
        generate_token_report(analyzer, "test_complex.c", None, report_generator)
        
    # 添加分页
    report_generator.add_page_break()
    
    # 分析题目示例
    identifiers.clear()
    constants.clear()
    analyzer = LexicalAnalyzer()
    analyzer.load_string("""If i=0 then n++;
a<= 3b %);""")
    analyzer.analyze()
    generate_token_report(analyzer, None, "题目中的测试例子", report_generator)
    
    # 生成PDF
    report_generator.build()
    
    return "词法分析综合报告.pdf"

def main():
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("用法: python report_generator.py <源程序文件> [输出PDF文件]")
        print("或使用: python report_generator.py --all (生成所有示例的综合报告)")
        return
        
    if sys.argv[1] == "--all":
        output_path = generate_report_from_examples()
        print(f"综合报告已生成: {output_path}")
    else:
        input_file = sys.argv[1]
        output_path = sys.argv[2] if len(sys.argv) > 2 else None
        output_path = generate_report_from_file(input_file, output_path)
        print(f"报告已生成: {output_path}")

if __name__ == "__main__":
    main() 