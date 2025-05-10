#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class LL1Parser:
    def __init__(self):
        # 定义终结符和非终结符
        self.terminals = ['+', '-', '*', '/', '(', ')', 'i', '#']
        self.non_terminals = ['E', 'G', 'T', 'S', 'F']
        
        # 定义文法规则
        self.grammar = {
            'E': [['T', 'G']],
            'G': [['+', 'T', 'G'], ['-', 'T', 'G'], ['ε']],
            'T': [['F', 'S']],
            'S': [['*', 'F', 'S'], ['/', 'F', 'S'], ['ε']],
            'F': [['(', 'E', ')'], ['i']]
        }
        
        # 初始化First集和Follow集
        self.first = {nt: set() for nt in self.non_terminals}
        self.follow = {nt: set() for nt in self.non_terminals}
        
        # 初始化分析表
        self.table = {}
        
        # 初始化分析栈和输入串
        self.stack = []
        self.input_string = ""
        
        # 计算First集、Follow集和构建分析表
        self.compute_first_sets()
        self.compute_follow_sets()
        self.build_parsing_table()
    
    def compute_first_sets(self):
        # 计算每个非终结符的First集
        changed = True
        while changed:
            changed = False
            for nt in self.non_terminals:
                for production in self.grammar[nt]:
                    # 如果产生式以终结符开始或者是空串
                    if production[0] in self.terminals or production[0] == 'ε':
                        if production[0] not in self.first[nt]:
                            self.first[nt].add(production[0])
                            changed = True
                    # 如果产生式以非终结符开始
                    elif production[0] in self.non_terminals:
                        # 添加非终结符的First集（不包括ε）
                        for symbol in self.first[production[0]]:
                            if symbol != 'ε' and symbol not in self.first[nt]:
                                self.first[nt].add(symbol)
                                changed = True
                        
                        # 处理可能的连续非终结符推导出ε的情况
                        all_can_derive_epsilon = True
                        for i, symbol in enumerate(production):
                            if symbol in self.terminals:
                                if symbol not in self.first[nt]:
                                    self.first[nt].add(symbol)
                                    changed = True
                                all_can_derive_epsilon = False
                                break
                            elif symbol in self.non_terminals:
                                # 添加非终结符的First集（不包括ε）
                                for s in self.first[symbol]:
                                    if s != 'ε' and s not in self.first[nt]:
                                        self.first[nt].add(s)
                                        changed = True
                                
                                # 如果这个非终结符不能推导出ε，就停止
                                if 'ε' not in self.first[symbol]:
                                    all_can_derive_epsilon = False
                                    break
                        
                        # 如果所有符号都可以推导出ε，则ε也是这个非终结符的First集的一部分
                        if all_can_derive_epsilon and 'ε' not in self.first[nt]:
                            self.first[nt].add('ε')
                            changed = True
    
    def compute_follow_sets(self):
        # 初始化Follow集，#是输入串的结束符号
        self.follow['E'].add('#')
        
        changed = True
        while changed:
            changed = False
            for nt in self.non_terminals:
                for head, productions in self.grammar.items():
                    for production in productions:
                        for i, symbol in enumerate(production):
                            if symbol == nt:  # 找到了非终结符
                                # 如果是产生式最后一个符号
                                if i == len(production) - 1:
                                    # 将头部非终结符的Follow集加入到当前非终结符的Follow集
                                    for s in self.follow[head]:
                                        if s not in self.follow[nt]:
                                            self.follow[nt].add(s)
                                            changed = True
                                else:
                                    next_symbol = production[i + 1]
                                    # 如果下一个符号是终结符
                                    if next_symbol in self.terminals:
                                        if next_symbol not in self.follow[nt]:
                                            self.follow[nt].add(next_symbol)
                                            changed = True
                                    # 如果下一个符号是非终结符
                                    elif next_symbol in self.non_terminals:
                                        # 将下一个符号的First集（不包括ε）加入到当前符号的Follow集
                                        for s in self.first[next_symbol]:
                                            if s != 'ε' and s not in self.follow[nt]:
                                                self.follow[nt].add(s)
                                                changed = True
                                        
                                        # 如果下一个符号的First集包含ε
                                        if 'ε' in self.first[next_symbol]:
                                            # 将头部非终结符的Follow集加入到当前非终结符的Follow集
                                            for s in self.follow[head]:
                                                if s not in self.follow[nt]:
                                                    self.follow[nt].add(s)
                                                    changed = True
    
    def build_parsing_table(self):
        # 初始化分析表
        for nt in self.non_terminals:
            self.table[nt] = {}
            for t in self.terminals:
                self.table[nt][t] = None
        
        # 填充分析表
        for nt in self.non_terminals:
            for production in self.grammar[nt]:
                # 获取产生式的First集
                first_of_production = self.get_first_of_production(production)
                
                for terminal in first_of_production:
                    if terminal != 'ε':
                        if self.table[nt][terminal] is None:
                            self.table[nt][terminal] = production
                        else:
                            print(f"文法不是LL(1)文法！在{nt}->{production}处产生冲突")
                
                # 如果产生式的First集包含空串，则需要考虑Follow集
                if 'ε' in first_of_production:
                    for terminal in self.follow[nt]:
                        if self.table[nt][terminal] is None:
                            self.table[nt][terminal] = production
                        else:
                            print(f"文法不是LL(1)文法！在{nt}->{production}处产生冲突")
    
    def get_first_of_production(self, production):
        # 获取产生式的First集
        if not production or production[0] == 'ε':
            return {'ε'}
        
        result = set()
        all_can_derive_epsilon = True
        
        for symbol in production:
            if symbol in self.terminals:
                result.add(symbol)
                all_can_derive_epsilon = False
                break
            elif symbol in self.non_terminals:
                for s in self.first[symbol]:
                    if s != 'ε':
                        result.add(s)
                
                if 'ε' not in self.first[symbol]:
                    all_can_derive_epsilon = False
                    break
        
        if all_can_derive_epsilon:
            result.add('ε')
        
        return result
    
    def parse(self, input_string):
        # 添加终止符
        self.input_string = input_string + '#'
        self.stack = ['#', 'E']  # 初始化栈，包含起始符号E和栈底标记#
        
        print("步骤\t分析栈\t\t剩余输入串\t所用产生式\t\t动作")
        step = 0
        
        # 打印初始状态
        print(f"{step}\t{self.stack}\t\t{self.input_string}\t初始化\t\t\t初始化")
        
        # 当前输入符号的索引
        index = 0
        
        while self.stack:
            step += 1
            
            # 获取栈顶元素和当前输入符号
            top = self.stack[-1]
            current_input = self.input_string[index]
            
            # 如果栈顶是终结符或#
            if top in self.terminals or top == '#':
                if top == current_input:  # 匹配成功
                    self.stack.pop()
                    index += 1
                    print(f"{step}\t{self.stack}\t\t{self.input_string[index:]}\t匹配 {top}\t\t\tPOP")
                else:  # 匹配失败
                    print(f"错误：栈顶终结符 {top} 与当前输入 {current_input} 不匹配")
                    return False
            
            # 如果栈顶是非终结符
            elif top in self.non_terminals:
                if self.table[top][current_input] is not None:  # 有对应的产生式
                    production = self.table[top][current_input]
                    self.stack.pop()
                    
                    # 如果产生式不是空串，则逆序入栈
                    if production != ['ε']:
                        for symbol in reversed(production):
                            self.stack.append(symbol)
                    
                    # 打印使用的产生式
                    production_str = f"{top} -> {''.join(production)}"
                    print(f"{step}\t{self.stack}\t\t{self.input_string[index:]}\t{production_str}\t\t\tPOP, PUSH({', '.join(reversed(production))})")
                else:  # 没有对应的产生式
                    print(f"错误：分析表中没有 [{top}, {current_input}] 对应的产生式")
                    return False
            else:
                print(f"错误：未知的栈顶符号 {top}")
                return False
            
            # 如果栈为空但输入未结束，或者栈不为空但输入已结束，则分析失败
            if (not self.stack and index < len(self.input_string) - 1) or (self.stack and index >= len(self.input_string)):
                print("错误：分析提前结束或输入不完整")
                return False
            
            # 如果栈顶和输入都是#，则分析成功
            if self.stack and index < len(self.input_string) and self.stack[-1] == '#' and self.input_string[index] == '#':
                print(f"{step}\t{self.stack}\t\t{self.input_string[index:]}\t接受\t\t\t成功")
                return True
        
        return True

def main():
    parser = LL1Parser()
    
    print("LL(1)语法分析程序")
    print("文法：")
    print("E -> TG")
    print("G -> +TG | -TG | ε")
    print("T -> FS")
    print("S -> *FS | /FS | ε")
    print("F -> (E) | i")
    print()
    
    while True:
        input_string = input("请输入要分析的表达式（输入'q'退出）：")
        if input_string.lower() == 'q':
            break
        
        print(f"\n开始分析表达式：{input_string}")
        result = parser.parse(input_string)
        
        if result:
            print("\n表达式分析成功！")
        else:
            print("\n表达式分析失败！")
        print()

if __name__ == "__main__":
    main() 