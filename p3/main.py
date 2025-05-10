#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from infix_to_postfix import InfixToPostfix
from postfix_calculator import PostfixCalculator
from debug_process import DebugProcess

def parse_variable_assignment(assignment):
    """解析变量赋值语句，如 'a=3'"""
    try:
        name, value = assignment.split('=')
        name = name.strip()
        value = float(value.strip())
        return name, value
    except:
        raise ValueError(f"变量赋值格式错误: '{assignment}'，正确格式应为 'name=value'")

def print_process_table(infix_expr, postfix_expr, variables, result):
    """打印处理过程表格"""
    print("\n" + "=" * 60)
    print("中缀表达式：", infix_expr)
    print("后缀表达式：", postfix_expr)
    print("-" * 60)
    print("变量赋值：")
    for name, value in variables.items():
        print(f"  {name} = {value}")
    print("-" * 60)
    print(f"计算结果: {result}")
    print("=" * 60)

def main():
    print("逆波兰表达式转换与计算程序")
    print("=" * 40)
    print("说明：")
    print("1. 输入中缀表达式，程序将转换为后缀表达式并计算结果")
    print("2. 支持的运算符: +, -, *, /, (, )")
    print("3. 负数使用括号，如 (-3) 或 (-a)")
    print("4. 使用 '#' 结束表达式输入")
    print("5. 输入 'q' 退出程序")
    print("=" * 40)
    
    infix_converter = InfixToPostfix()
    calculator = PostfixCalculator()
    debugger = DebugProcess()
    
    while True:
        print("\n请输入操作：")
        print("1. 中缀表达式转后缀表达式")
        print("2. 中缀表达式转后缀表达式并计算结果")
        print("3. 详细显示中缀转后缀的过程")
        print("4. 详细显示后缀表达式的计算过程")
        print("q. 退出程序")
        
        choice = input("请选择: ").strip()
        
        if choice.lower() == 'q':
            print("程序已退出")
            break
            
        if choice == '1':
            infix_expr = input("请输入中缀表达式 (以#结束): ").strip()
            if not infix_expr:
                print("表达式不能为空")
                continue
                
            try:
                postfix_expr = infix_converter.infix_to_postfix(infix_expr)
                print(f"后缀表达式: {postfix_expr}")
            except Exception as e:
                print(f"错误: {e}")
                
        elif choice == '2':
            infix_expr = input("请输入中缀表达式 (以#结束): ").strip()
            if not infix_expr:
                print("表达式不能为空")
                continue
                
            try:
                postfix_expr = infix_converter.infix_to_postfix(infix_expr)
                print(f"后缀表达式: {postfix_expr}")
                
                # 变量赋值
                print("请输入变量赋值 (如 'a=3;b=5;c=2;'，以空行结束):")
                variables = {}
                while True:
                    line = input().strip()
                    if not line:
                        break
                    
                    # 处理多个变量赋值
                    for assignment in line.rstrip(';').split(';'):
                        if assignment.strip():
                            name, value = parse_variable_assignment(assignment)
                            calculator.set_variable(name, value)
                            variables[name] = value
                
                # 计算结果
                result = calculator.evaluate_postfix(postfix_expr)
                print_process_table(infix_expr, postfix_expr, variables, result)
                
            except Exception as e:
                print(f"错误: {e}")
                
        elif choice == '3':
            infix_expr = input("请输入中缀表达式 (以#结束): ").strip()
            if not infix_expr:
                print("表达式不能为空")
                continue
                
            try:
                postfix_expr, process_table = debugger.trace_infix_to_postfix(infix_expr)
                print(f"中缀表达式: {infix_expr}")
                print(f"后缀表达式: {postfix_expr}")
                debugger.print_infix_to_postfix_table(process_table)
            except Exception as e:
                print(f"错误: {e}")
                
        elif choice == '4':
            infix_expr = input("请输入中缀表达式 (以#结束): ").strip()
            if not infix_expr:
                print("表达式不能为空")
                continue
                
            try:
                postfix_expr = infix_converter.infix_to_postfix(infix_expr)
                print(f"中缀表达式: {infix_expr}")
                print(f"后缀表达式: {postfix_expr}")
                
                # 变量赋值
                print("请输入变量赋值 (如 'a=3;b=5;c=2;'，以空行结束):")
                variables = {}
                while True:
                    line = input().strip()
                    if not line:
                        break
                    
                    # 处理多个变量赋值
                    for assignment in line.rstrip(';').split(';'):
                        if assignment.strip():
                            name, value = parse_variable_assignment(assignment)
                            variables[name] = value
                
                # 计算结果并显示过程
                result, eval_process = debugger.trace_postfix_evaluation(postfix_expr, variables)
                
                print(f"\n变量赋值:")
                for name, value in variables.items():
                    print(f"  {name} = {value}")
                
                debugger.print_postfix_evaluation_table(eval_process)
                print(f"\n计算结果: {result}")
                
            except Exception as e:
                print(f"错误: {e}")
        else:
            print("无效的选项，请重新输入")

if __name__ == "__main__":
    main() 