#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class PostfixCalculator:
    def __init__(self):
        # 存储变量的字典
        self.variables = {}
        
    def set_variable(self, name, value):
        """设置变量的值"""
        self.variables[name] = value
        
    def get_variable(self, name):
        """获取变量的值"""
        if name in self.variables:
            return self.variables[name]
        else:
            raise ValueError(f"变量 {name} 未定义")
    
    def is_number(self, token):
        """判断字符串是否可以转换为数字"""
        try:
            float(token)
            return True
        except ValueError:
            return False
            
    def evaluate_postfix(self, postfix_expr):
        """计算逆波兰表达式的值"""
        stack = []
        
        i = 0
        while i < len(postfix_expr):
            token = postfix_expr[i]
            
            # 处理多字符的数字或变量
            if token.isalnum():
                temp = token
                i += 1
                while i < len(postfix_expr) and postfix_expr[i].isalnum():
                    temp += postfix_expr[i]
                    i += 1
                
                # 处理数字或变量
                if self.is_number(temp):
                    stack.append(float(temp))
                else:
                    stack.append(self.get_variable(temp))
                continue
            
            # 处理运算符
            if token in "+-*/":
                if len(stack) < 2:
                    raise ValueError("表达式错误：运算符缺少操作数")
                
                b = stack.pop()
                a = stack.pop()
                
                if token == '+':
                    stack.append(a + b)
                elif token == '-':
                    stack.append(a - b)
                elif token == '*':
                    stack.append(a * b)
                elif token == '/':
                    if b == 0:
                        raise ZeroDivisionError("除数不能为零")
                    stack.append(a / b)
            
            # 处理一元负号
            elif token == '@':
                if not stack:
                    raise ValueError("表达式错误：一元运算符缺少操作数")
                a = stack.pop()
                stack.append(-a)
            
            i += 1
            
        if len(stack) != 1:
            raise ValueError("表达式错误：操作数过多")
            
        return stack[0] 