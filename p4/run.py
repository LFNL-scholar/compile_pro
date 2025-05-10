#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# LR(1)分析器启动脚本

import sys
import os
import argparse

def main():
    parser = argparse.ArgumentParser(description='LR(1)语法分析器')
    parser.add_argument('--cli', action='store_true', help='使用命令行界面')
    parser.add_argument('--batch', action='store_true', help='批量测试模式')
    parser.add_argument('--file', type=str, default='test_cases.txt', help='指定测试用例文件')
    
    args = parser.parse_args()
    
    if args.cli:
        # 命令行模式
        from lr1_parser import main as lr1_main
        lr1_main()
    elif args.batch:
        # 批量测试模式
        from batch_test import main as batch_main
        sys.argv = [sys.argv[0]]
        if args.file:
            sys.argv.append(args.file)
        batch_main()
    else:
        # GUI模式
        from lr1_gui import main as gui_main
        gui_main()

if __name__ == "__main__":
    main() 