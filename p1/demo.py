#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
词法分析器演示程序
"""

from lexical_analyzer import LexicalAnalyzer

def analyze_file(filename):
    """分析指定的文件并打印结果"""
    print(f"\n分析文件: {filename}")
    print("=" * 50)
    
    analyzer = LexicalAnalyzer()
    if analyzer.load_file(filename):
        analyzer.analyze()
        analyzer.print_results()
        
        # 打印统计信息
        print("\n分析统计:")
        from lexical_analyzer import identifiers, constants
        print(f"标识符表: {identifiers}")
        print(f"常数表: {constants}")
        print(f"错误数量: {analyzer.error_count}")
    else:
        print(f"无法打开文件: {filename}")

def analyze_code(code, description):
    """分析指定的代码字符串并打印结果"""
    print(f"\n分析代码: {description}")
    print("=" * 50)
    
    analyzer = LexicalAnalyzer()
    analyzer.load_string(code)
    analyzer.analyze()
    analyzer.print_results()
    
    # 打印统计信息
    print("\n分析统计:")
    from lexical_analyzer import identifiers, constants
    print(f"标识符表: {identifiers}")
    print(f"常数表: {constants}")
    print(f"错误数量: {analyzer.error_count}")

def main():
    # 清空原有的标识符和常数表
    from lexical_analyzer import identifiers, constants
    identifiers.clear()
    constants.clear()
    
    # 分析简单的测试文件
    analyze_file("test.c")
    
    # 分析复杂的测试文件
    identifiers.clear()
    constants.clear()
    analyze_file("test_complex.c")
    
    # 分析测试例子
    identifiers.clear()
    constants.clear()
    analyze_code("""If i=0 then n++;
a<= 3b %);""", "题目中的测试例子")

if __name__ == "__main__":
    main() 