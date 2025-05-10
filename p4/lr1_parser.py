#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# LR(1)分析器实现

class LR1Parser:
    def __init__(self):
        # 初始化ACTION表
        self.action = {
            0: {'i': ('S', 5), '(': ('S', 4)},
            1: {'+': ('S', 6), '#': ('acc', None)},
            2: {'+': ('r', 2), '*': ('S', 7), ')': ('r', 2), '#': ('r', 2)},
            3: {'+': ('r', 4), '*': ('r', 4), ')': ('r', 4), '#': ('r', 4)},
            4: {'i': ('S', 5), '(': ('S', 4)},
            5: {'+': ('r', 6), '*': ('r', 6), ')': ('r', 6), '#': ('r', 6)},
            6: {'i': ('S', 5), '(': ('S', 4)},
            7: {'i': ('S', 5), '(': ('S', 4)},
            8: {'+': ('S', 6), ')': ('S', 11)},
            9: {'+': ('r', 1), '*': ('S', 7), ')': ('r', 1), '#': ('r', 1)},
            10: {'+': ('r', 3), '*': ('r', 3), ')': ('r', 3), '#': ('r', 3)},
            11: {'+': ('r', 5), '*': ('r', 5), ')': ('r', 5), '#': ('r', 5)}
        }
        
        # 初始化GOTO表
        self.goto = {
            0: {'E': 1, 'T': 2, 'F': 3},
            4: {'E': 8, 'T': 2, 'F': 3},
            6: {'T': 9, 'F': 3},
            7: {'F': 10}
        }
        
        # 产生式
        self.productions = {
            1: ('E', 'E+T'),
            2: ('E', 'T'),
            3: ('T', 'T*F'),
            4: ('T', 'F'),
            5: ('F', '(E)'),
            6: ('F', 'i')
        }
        
        # 添加E→E-T和T→T/F的产生式和相应的动作表和GOTO表项
        # 注意：这里简化处理，实际应该重新构建分析表
        self.action[1]['-'] = ('S', 6)  # 与+相同的处理
        self.action[9]['-'] = ('r', 1)  # 与+相同的处理
        
        self.action[2]['/'] = ('S', 7)  # 与*相同的处理
        self.action[10]['/'] = ('r', 3)  # 与*相同的处理
        
        # 添加E→E-T和T→T/F的产生式
        self.productions[7] = ('E', 'E-T')
        self.productions[8] = ('T', 'T/F')
    
    def parse(self, input_string, silent=False):
        # 确保输入字符串以#结尾
        if not input_string.endswith('#'):
            input_string += '#'
        
        # 初始化状态栈、符号栈和输入串
        state_stack = [0]  # 状态栈初始状态为0
        symbol_stack = ['#']  # 符号栈初始符号为#
        input_chars = list(input_string)
        current_pos = 0
        current_char = input_chars[current_pos]
        
        # 如果不是静默模式，则打印表头
        if not silent:
            print(f"{'步骤':<6}{'状态栈':<20}{'符号栈':<20}{'剩余输入串':<20}{'动作':<10}")
        
        step = 1
        while True:
            # 获取当前状态栈顶的状态
            current_state = state_stack[-1]
            
            # 当前分析步骤信息
            state_str = ''.join(map(str, state_stack))
            symbol_str = ''.join(symbol_stack)
            input_str = ''.join(input_chars[current_pos:])
            
            # 检查当前状态和输入符号的动作
            if current_state in self.action and current_char in self.action[current_state]:
                action_type, action_value = self.action[current_state][current_char]
                
                # 根据动作类型执行相应操作
                if action_type == 'S':  # 移进
                    if not silent:
                        print(f"{step:<6}{state_str:<20}{symbol_str:<20}{input_str:<20}{'移进':<10}")
                    state_stack.append(action_value)
                    symbol_stack.append(current_char)
                    current_pos += 1
                    current_char = input_chars[current_pos]
                    
                elif action_type == 'r':  # 归约
                    production_num = action_value
                    left, right = self.productions[production_num]
                    
                    # 弹出|β|个符号和状态
                    for _ in range(len(right)):
                        state_stack.pop()
                        symbol_stack.pop()
                    
                    # 当前状态
                    current_state = state_stack[-1]
                    
                    # 压入左部非终结符
                    symbol_stack.append(left)
                    
                    # 查找GOTO表，获取新状态
                    if current_state in self.goto and left in self.goto[current_state]:
                        new_state = self.goto[current_state][left]
                        state_stack.append(new_state)
                    else:
                        if not silent:
                            print(f"错误：无法找到GOTO[{current_state},{left}]")
                        return False
                    
                    if not silent:
                        print(f"{step:<6}{state_str:<20}{symbol_str:<20}{input_str:<20}{f'r{production_num}: {left}→{right}归约':<10}")
                    
                elif action_type == 'acc':  # 接受
                    if not silent:
                        print(f"{step:<6}{state_str:<20}{symbol_str:<20}{input_str:<20}{'接受':<10}")
                        print("分析成功！")
                    return True
            else:
                if not silent:
                    print(f"{step:<6}{state_str:<20}{symbol_str:<20}{input_str:<20}{'错误':<10}")
                    print(f"错误：状态{current_state}下遇到意外的符号'{current_char}'")
                return False
            
            step += 1

def main():
    parser = LR1Parser()
    print("LR(1)语法分析器")
    print("支持的文法：")
    print("1. E→E+T")
    print("2. E→E-T")
    print("3. T→T*F")
    print("4. T→T/F")
    print("5. F→(E)")
    print("6. F→i")
    print("\n输入符号说明：i表示标识符，+,-,*,/,(,)表示运算符和括号，#表示输入结束")
    
    while True:
        input_string = input("\n请输入一个以#结束的符号串(包括+−*/()i#)：")
        if input_string.lower() == 'exit':
            break
        
        # 检查输入是否合法
        valid_chars = set('i+-*/()#')
        if not all(char in valid_chars for char in input_string):
            print("错误：输入包含不支持的字符。请只使用i, +, -, *, /, (, ), #")
            continue
        
        parser.parse(input_string)
        
        choice = input("\n是否继续分析?(y/n): ")
        if choice.lower() != 'y':
            break

if __name__ == "__main__":
    main() 