#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class InfixToPostfix:
    def __init__(self):
        # 运算符优先级定义
        self.priority = {
            '+': 1,
            '-': 1,
            '*': 2,
            '/': 2,
            '(': 0,
            ')': 0,
            '#': -1
        }
        
    def is_operator(self, char):
        """判断字符是否为运算符"""
        return char in '+-*/()#'
        
    def is_number_or_letter(self, char):
        """判断字符是否为数字或字母"""
        return char.isalnum()
    
    def get_priority(self, operator):
        """获取运算符优先级"""
        return self.priority.get(operator, 0)
    
    def higher_priority(self, op1, op2):
        """比较两个运算符的优先级"""
        return self.get_priority(op1) >= self.get_priority(op2)
    
    def infix_to_postfix(self, infix_expr):
        """将中缀表达式转换为后缀表达式（逆波兰表达式）"""
        if not infix_expr.endswith('#'):
            infix_expr += '#'
            
        stack = []  # 运算符栈
        postfix = []  # 后缀表达式
        i = 0
        
        while i < len(infix_expr):
            char = infix_expr[i]
            
            # 处理数字或字母
            if self.is_number_or_letter(char):
                # 收集完整的数字或标识符
                num_str = char
                i += 1
                while i < len(infix_expr) and self.is_number_or_letter(infix_expr[i]):
                    num_str += infix_expr[i]
                    i += 1
                postfix.append(num_str)
                continue
            
            # 处理特殊情况：负号
            if char == '-' and (i == 0 or infix_expr[i-1] == '(' or self.is_operator(infix_expr[i-1])):
                # 将负号视为一元运算符，用'@'表示
                stack.append('@')
                i += 1
                continue
                
            # 处理运算符
            if self.is_operator(char):
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
                    while stack and stack[-1] != '(' and self.higher_priority(stack[-1], char):
                        postfix.append(stack.pop())
                    stack.append(char)
            
            i += 1
            
        # 将后缀表达式列表转换为字符串
        return ''.join(postfix) 