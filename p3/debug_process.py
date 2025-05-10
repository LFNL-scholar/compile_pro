#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from infix_to_postfix import InfixToPostfix
from postfix_calculator import PostfixCalculator

class DebugProcess:
    def __init__(self):
        self.converter = InfixToPostfix()
        self.calculator = PostfixCalculator()
        
    def trace_infix_to_postfix(self, infix_expr):
        """追踪中缀表达式转换为后缀表达式的过程"""
        if not infix_expr.endswith('#'):
            infix_expr += '#'
            
        stack = []  # 运算符栈
        postfix = []  # 后缀表达式
        process_table = []  # 处理过程表
        
        i = 0
        remainder = infix_expr
        
        while i < len(infix_expr):
            char = infix_expr[i]
            current_stack = stack.copy()
            current_postfix = ''.join(postfix)
            
            # 记录当前状态
            process_table.append({
                "步骤": len(process_table),
                "当前符号": char,
                "输入区": remainder[1:] if i < len(remainder) else "",
                "运算符栈": ''.join(current_stack),
                "输出区": current_postfix
            })
            
            # 处理数字或字母
            if self.converter.is_number_or_letter(char):
                # 收集完整的数字或标识符
                num_str = char
                i += 1
                while i < len(infix_expr) and self.converter.is_number_or_letter(infix_expr[i]):
                    num_str += infix_expr[i]
                    i += 1
                postfix.append(num_str)
                remainder = infix_expr[i:]
                continue
            
            # 处理特殊情况：负号
            if char == '-' and (i == 0 or infix_expr[i-1] == '(' or self.converter.is_operator(infix_expr[i-1])):
                # 将负号视为一元运算符，用'@'表示
                stack.append('@')
                i += 1
                remainder = infix_expr[i:]
                continue
                
            # 处理运算符
            if self.converter.is_operator(char):
                if char == '(':
                    stack.append(char)
                elif char == ')':
                    # 弹出所有操作符直到遇到左括号
                    while stack and stack[-1] != '(':
                        postfix.append(stack.pop())
                    if stack and stack[-1] == '(':
                        stack.pop()  # 弹出左括号
                elif char == '#':
                    # 处理结束符号，弹出所有运算符
                    while stack:
                        postfix.append(stack.pop())
                else:
                    # 处理普通运算符
                    while stack and stack[-1] != '(' and self.converter.higher_priority(stack[-1], char):
                        postfix.append(stack.pop())
                    stack.append(char)
            
            i += 1
            remainder = infix_expr[i:] if i < len(infix_expr) else ""
        
        # 记录最终状态
        process_table.append({
            "步骤": len(process_table),
            "当前符号": "",
            "输入区": "",
            "运算符栈": ''.join(stack),
            "输出区": ''.join(postfix)
        })
        
        return ''.join(postfix), process_table
    
    def trace_postfix_evaluation(self, postfix_expr, variables=None):
        """追踪后缀表达式计算的过程"""
        if variables is None:
            variables = {}
            
        for name, value in variables.items():
            self.calculator.set_variable(name, value)
            
        stack = []
        process_table = []
        
        i = 0
        while i < len(postfix_expr):
            token = postfix_expr[i]
            
            # 记录当前状态
            process_table.append({
                "步骤": len(process_table),
                "当前符号": token,
                "栈内容": stack.copy()
            })
            
            # 处理多字符的数字或变量
            if token.isalnum():
                temp = token
                i += 1
                while i < len(postfix_expr) and postfix_expr[i].isalnum():
                    temp += postfix_expr[i]
                    i += 1
                
                # 处理数字或变量
                if self.calculator.is_number(temp):
                    stack.append(float(temp))
                else:
                    value = self.calculator.get_variable(temp)
                    stack.append(value)
                    process_table[-1]["说明"] = f"{temp} = {value}"
                continue
            
            # 处理运算符
            if token in "+-*/":
                if len(stack) < 2:
                    raise ValueError("表达式错误：运算符缺少操作数")
                
                b = stack.pop()
                a = stack.pop()
                
                if token == '+':
                    result = a + b
                    stack.append(result)
                    process_table[-1]["说明"] = f"{a} + {b} = {result}"
                elif token == '-':
                    result = a - b
                    stack.append(result)
                    process_table[-1]["说明"] = f"{a} - {b} = {result}"
                elif token == '*':
                    result = a * b
                    stack.append(result)
                    process_table[-1]["说明"] = f"{a} * {b} = {result}"
                elif token == '/':
                    if b == 0:
                        raise ZeroDivisionError("除数不能为零")
                    result = a / b
                    stack.append(result)
                    process_table[-1]["说明"] = f"{a} / {b} = {result}"
            
            # 处理一元负号
            elif token == '@':
                if not stack:
                    raise ValueError("表达式错误：一元运算符缺少操作数")
                a = stack.pop()
                result = -a
                stack.append(result)
                process_table[-1]["说明"] = f"-({a}) = {result}"
            
            i += 1
        
        # 记录最终状态
        if stack:
            process_table.append({
                "步骤": len(process_table),
                "当前符号": "结果",
                "栈内容": stack.copy(),
                "说明": f"最终结果: {stack[0]}"
            })
            
        if len(stack) != 1:
            raise ValueError("表达式错误：操作数过多")
            
        return stack[0], process_table
    
    def print_infix_to_postfix_table(self, process_table):
        """打印中缀转后缀的过程表格"""
        print("\n" + "=" * 80)
        print("中缀表达式转后缀表达式过程表:")
        print("-" * 80)
        print(f"{'步骤':^5} | {'当前符号':^8} | {'输入区':^20} | {'运算符栈':^15} | {'输出区':^20}")
        print("-" * 80)
        
        for row in process_table:
            print(f"{row['步骤']:^5} | {row['当前符号']:^8} | {row['输入区']:^20} | {row['运算符栈']:^15} | {row['输出区']:^20}")
        
        print("=" * 80)
    
    def print_postfix_evaluation_table(self, process_table):
        """打印后缀表达式计算的过程表格"""
        print("\n" + "=" * 80)
        print("后缀表达式计算过程表:")
        print("-" * 80)
        print(f"{'步骤':^5} | {'当前符号':^8} | {'栈内容':^30} | {'说明':^30}")
        print("-" * 80)
        
        for row in process_table:
            stack_str = ', '.join(str(x) for x in row['栈内容'])
            explanation = row.get('说明', '')
            print(f"{row['步骤']:^5} | {row['当前符号']:^8} | {stack_str:^30} | {explanation:^30}")
        
        print("=" * 80)

# 单独测试
if __name__ == "__main__":
    debug = DebugProcess()
    
    infix_expr = "(a+b*c)*d#"
    postfix_expr, process_table = debug.trace_infix_to_postfix(infix_expr)
    
    print(f"中缀表达式: {infix_expr}")
    print(f"后缀表达式: {postfix_expr}")
    debug.print_infix_to_postfix_table(process_table)
    
    variables = {'a': 2, 'b': 3, 'c': 4, 'd': 5}
    result, eval_process = debug.trace_postfix_evaluation(postfix_expr, variables)
    
    print(f"\n变量赋值:")
    for name, value in variables.items():
        print(f"  {name} = {value}")
    
    debug.print_postfix_evaluation_table(eval_process)
    print(f"\n计算结果: {result}") 