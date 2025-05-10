#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# LR(1)分析器批量测试工具

from lr1_parser import LR1Parser
import sys

def run_batch_test(test_file):
    """
    批量测试LR(1)分析器
    
    参数:
        test_file: 测试用例文件路径
    """
    parser = LR1Parser()
    
    try:
        with open(test_file, 'r') as f:
            test_cases = f.readlines()
    except FileNotFoundError:
        print(f"错误: 无法找到测试文件 '{test_file}'")
        return
    
    print("=" * 60)
    print("LR(1)分析器批量测试")
    print("=" * 60)
    
    case_num = 0
    for line in test_cases:
        line = line.strip()
        # 跳过空行和注释行
        if not line or line.startswith('#'):
            continue
        
        case_num += 1
        print(f"\n测试用例 {case_num}: {line}")
        print("-" * 60)
        
        result = parser.parse(line)
        
        print("-" * 60)
        if result:
            print(f"用例 {case_num} 结果: 成功 ✓")
        else:
            print(f"用例 {case_num} 结果: 失败 ✗")
        
        print("=" * 60)
    
    print(f"\n总共测试了 {case_num} 个用例。")

def main():
    # 默认测试文件
    test_file = "test_cases.txt"
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        test_file = sys.argv[1]
    
    run_batch_test(test_file)

if __name__ == "__main__":
    main() 