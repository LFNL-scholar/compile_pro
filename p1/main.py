#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
词法分析器程序入口
提供命令行和图形界面两种使用方式
"""

import sys
import os
import argparse
from PyQt6.QtWidgets import QApplication

# 导入词法分析器模块
from lexical_analyzer import LexicalAnalyzer, main as analyzer_cli
from lexical_analyzer_ui import LexicalAnalyzerUI

def main():
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='词法分析器')
    parser.add_argument('-f', '--file', help='要分析的源代码文件')
    parser.add_argument('-c', '--cli', action='store_true', help='使用命令行界面')
    parser.add_argument('-g', '--gui', action='store_true', help='使用图形用户界面')
    
    args = parser.parse_args()
    
    # 如果指定了--cli参数或者指定了输入文件但没有指定界面类型，则使用命令行界面
    if args.cli or (args.file and not args.gui):
        # 如果提供了文件参数，将其传递给命令行工具
        if args.file:
            sys.argv = [sys.argv[0], args.file]
        analyzer_cli()
    else:
        # 默认使用图形界面
        app = QApplication(sys.argv)
        window = LexicalAnalyzerUI()
        
        # 如果提供了文件参数，自动加载该文件
        if args.file and os.path.isfile(args.file):
            try:
                with open(args.file, 'r', encoding='utf-8') as f:
                    window.code_editor.setText(f.read())
                window.status_bar.showMessage(f'已加载文件: {args.file}')
            except Exception as e:
                print(f"无法打开文件: {e}")
        
        window.show()
        sys.exit(app.exec())

if __name__ == "__main__":
    main() 