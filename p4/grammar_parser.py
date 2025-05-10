#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 文法解析器，用于解析用户输入的文法并构建LR分析表

class GrammarParser:
    def __init__(self):
        self.terminals = set()  # 终结符集合
        self.non_terminals = set()  # 非终结符集合
        self.productions = []  # 产生式列表
        self.start_symbol = None  # 开始符号
        self.first_sets = {}  # FIRST集合
        self.follow_sets = {}  # FOLLOW集合
        self.augmented_grammar = None  # 增广文法
    
    def parse_grammar(self, grammar_text):
        """
        解析文法定义
        
        参数:
            grammar_text: 文法定义字符串，每行一个产生式，格式为 A → α | β | γ
        
        返回:
            bool: 解析是否成功
        """
        print("解析文法...")
        lines = grammar_text.strip().split('\n')
        
        # 处理每一行
        for line in lines:
            if not line.strip() or line.strip().startswith('#'):
                continue
                
            # 分离左部和右部
            if '->' not in line and '→' not in line:
                print(f"错误: 产生式格式不正确，缺少箭头: {line}")
                return False
                
            # 处理箭头可能是ASCII的->或者Unicode的→
            parts = line.split('->')
            if len(parts) == 1:
                parts = line.split('→')
                
            if len(parts) != 2:
                print(f"错误: 产生式格式不正确: {line}")
                return False
                
            left = parts[0].strip()
            right = parts[1].strip()
            
            # 添加非终结符
            self.non_terminals.add(left)
            
            # 如果还没有定义开始符号，则将第一个非终结符作为开始符号
            if self.start_symbol is None:
                self.start_symbol = left
                
            # 处理右部，支持 | 分隔的多个产生式
            alternatives = right.split('|')
            for alt in alternatives:
                alt = alt.strip()
                if not alt:  # 空产生式，使用epsilon(ε)表示
                    self.productions.append((left, 'ε'))
                else:
                    # 添加产生式
                    self.productions.append((left, alt))
                    
                    # 识别终结符和非终结符
                    for symbol in alt:
                        if symbol.isupper():  # 假设非终结符是大写字母
                            self.non_terminals.add(symbol)
                        elif symbol != ' ':  # 忽略空格
                            self.terminals.add(symbol)
        
        # 将终结符从非终结符集合中移除（防止重复）
        self.non_terminals = self.non_terminals - self.terminals
        
        # 添加终止符
        self.terminals.add('#')
        
        print("文法解析成功！")
        print(f"非终结符: {', '.join(sorted(self.non_terminals))}")
        print(f"终结符: {', '.join(sorted(self.terminals))}")
        print("产生式:")
        for i, (left, right) in enumerate(self.productions, 1):
            print(f"{i}. {left} → {right}")
        
        # 创建增广文法
        self.create_augmented_grammar()
        
        return True
    
    def create_augmented_grammar(self):
        """创建增广文法（添加S' → S）"""
        if self.start_symbol:
            # 增广文法的开始符号
            augmented_start = f"{self.start_symbol}'"
            self.non_terminals.add(augmented_start)
            
            # 增广产生式
            self.augmented_grammar = [(augmented_start, self.start_symbol)]
            self.augmented_grammar.extend(self.productions)
            
            print(f"\n增广文法:")
            print(f"0. {augmented_start} → {self.start_symbol}")
            for i, (left, right) in enumerate(self.productions, 1):
                print(f"{i}. {left} → {right}")
    
    def compute_first_sets(self):
        """
        计算所有符号的FIRST集合
        FIRST(X)表示从符号X推导出的所有句型的首符号集合
        """
        # 初始化FIRST集合
        self.first_sets = {symbol: set() for symbol in self.non_terminals}
        
        # 所有终结符的FIRST集合就是自身
        for t in self.terminals:
            self.first_sets[t] = {t}
        
        # 空串的FIRST集合是自身
        if 'ε' not in self.first_sets:
            self.first_sets['ε'] = {'ε'}
        
        # 计算非终结符的FIRST集合（不断迭代直到不再变化）
        changed = True
        while changed:
            changed = False
            
            for left, right in self.productions:
                # 跳过增广产生式
                if left.endswith("'") and len(left) > 1:
                    continue
                
                # 如果右部是空串，则将空串加入FIRST(left)
                if right == 'ε':
                    if 'ε' not in self.first_sets[left]:
                        self.first_sets[left].add('ε')
                        changed = True
                    continue
                
                # 取右部第一个符号
                first_symbol = right[0]
                
                # 如果第一个符号是终结符，则加入FIRST(left)
                if first_symbol in self.terminals:
                    if first_symbol not in self.first_sets[left]:
                        self.first_sets[left].add(first_symbol)
                        changed = True
                # 如果第一个符号是非终结符，则将其FIRST集合（不包括ε）加入FIRST(left)
                elif first_symbol in self.non_terminals:
                    for symbol in self.first_sets[first_symbol] - {'ε'}:
                        if symbol not in self.first_sets[left]:
                            self.first_sets[left].add(symbol)
                            changed = True
                    
                    # 如果第一个符号可以推导出空串，则继续处理下一个符号
                    i = 0
                    while i < len(right) and 'ε' in self.first_sets.get(right[i], set()):
                        i += 1
                        if i < len(right):
                            next_symbol = right[i]
                            if next_symbol in self.terminals:
                                if next_symbol not in self.first_sets[left]:
                                    self.first_sets[left].add(next_symbol)
                                    changed = True
                            elif next_symbol in self.non_terminals:
                                for symbol in self.first_sets[next_symbol] - {'ε'}:
                                    if symbol not in self.first_sets[left]:
                                        self.first_sets[left].add(symbol)
                                        changed = True
                    
                    # 如果所有符号都可以推导出空串，则将空串加入FIRST(left)
                    if i == len(right) and all('ε' in self.first_sets.get(s, set()) for s in right):
                        if 'ε' not in self.first_sets[left]:
                            self.first_sets[left].add('ε')
                            changed = True
        
        print("\nFIRST集合:")
        for symbol in sorted(self.first_sets.keys()):
            print(f"FIRST({symbol}) = {{{', '.join(sorted(self.first_sets[symbol]))}}}")
    
    def compute_follow_sets(self):
        """
        计算所有非终结符的FOLLOW集合
        FOLLOW(A)表示在某些句型中紧跟在A后面的终结符集合
        """
        # 初始化FOLLOW集合
        self.follow_sets = {nt: set() for nt in self.non_terminals}
        
        # 将#加入到开始符号的FOLLOW集合中
        if self.start_symbol:
            self.follow_sets[self.start_symbol].add('#')
        
        # 计算FOLLOW集合（不断迭代直到不再变化）
        changed = True
        while changed:
            changed = False
            
            for left, right in self.productions:
                # 跳过增广产生式和空产生式
                if (left.endswith("'") and len(left) > 1) or right == 'ε':
                    continue
                
                # 处理右部中的每个非终结符
                for i, symbol in enumerate(right):
                    if symbol in self.non_terminals:
                        # 如果该非终结符后面还有符号
                        if i < len(right) - 1:
                            next_symbol = right[i+1]
                            
                            # 将FIRST(next_symbol) - {ε}加入FOLLOW(symbol)
                            if next_symbol in self.first_sets:
                                for term in self.first_sets[next_symbol] - {'ε'}:
                                    if term not in self.follow_sets[symbol]:
                                        self.follow_sets[symbol].add(term)
                                        changed = True
                            
                            # 如果next_symbol可以推导出空串，将FOLLOW(left)加入FOLLOW(symbol)
                            if 'ε' in self.first_sets.get(next_symbol, set()):
                                for term in self.follow_sets[left]:
                                    if term not in self.follow_sets[symbol]:
                                        self.follow_sets[symbol].add(term)
                                        changed = True
                        
                        # 如果该非终结符是右部的最后一个符号，或者后面所有符号都可以推导出空串
                        # 则将FOLLOW(left)加入FOLLOW(symbol)
                        elif i == len(right) - 1:
                            for term in self.follow_sets[left]:
                                if term not in self.follow_sets[symbol]:
                                    self.follow_sets[symbol].add(term)
                                    changed = True
        
        print("\nFOLLOW集合:")
        for symbol in sorted(self.follow_sets.keys()):
            print(f"FOLLOW({symbol}) = {{{', '.join(sorted(self.follow_sets[symbol]))}}}")
    
    def generate_lr_tables(self):
        """
        生成LR分析表
        这里只是一个简化版，实际上LR(1)分析表的构建非常复杂
        完全实现需要构建项目集规范族等
        
        返回:
            tuple: (ACTION表, GOTO表)
        """
        print("\n警告: 自动生成LR分析表功能尚未完全实现。")
        print("这是一个复杂的过程，需要构建项目集规范族和计算闭包等。")
        print("目前只能用于简单文法。")
        
        # 这里只实现一个非常简化的版本，仅供演示
        # 真正的实现需要构建项目集规范族、计算闭包、构建ACTION和GOTO表等
        
        # 为了简单起见，我们假设这是一个简单的算术表达式文法
        # 并返回一个预定义的分析表
        action = {
            0: {'i': ('S', 5), '(': ('S', 4)},
            1: {'+': ('S', 6), '-': ('S', 6), '#': ('acc', None)},
            2: {'+': ('r', 2), '-': ('r', 2), '*': ('S', 7), '/': ('S', 7), ')': ('r', 2), '#': ('r', 2)},
            3: {'+': ('r', 4), '-': ('r', 4), '*': ('r', 4), '/': ('r', 4), ')': ('r', 4), '#': ('r', 4)},
            4: {'i': ('S', 5), '(': ('S', 4)},
            5: {'+': ('r', 6), '-': ('r', 6), '*': ('r', 6), '/': ('r', 6), ')': ('r', 6), '#': ('r', 6)},
            6: {'i': ('S', 5), '(': ('S', 4)},
            7: {'i': ('S', 5), '(': ('S', 4)},
            8: {'+': ('S', 6), '-': ('S', 6), ')': ('S', 11)},
            9: {'+': ('r', 1), '-': ('r', 1), '*': ('S', 7), '/': ('S', 7), ')': ('r', 1), '#': ('r', 1)},
            10: {'+': ('r', 3), '-': ('r', 3), '*': ('r', 3), '/': ('r', 3), ')': ('r', 3), '#': ('r', 3)},
            11: {'+': ('r', 5), '-': ('r', 5), '*': ('r', 5), '/': ('r', 5), ')': ('r', 5), '#': ('r', 5)}
        }
        
        goto = {
            0: {'E': 1, 'T': 2, 'F': 3},
            4: {'E': 8, 'T': 2, 'F': 3},
            6: {'T': 9, 'F': 3},
            7: {'F': 10}
        }
        
        print("\n如果需要为特定文法生成精确的LR分析表，需要进一步开发。")
        return action, goto

def main():
    parser = GrammarParser()
    
    print("文法解析器 - 用于解析用户输入的文法并构建LR分析表")
    print("=" * 60)
    print("请输入文法定义，每行一个产生式，格式为 A → α | β | γ")
    print("输入空行结束输入。")
    print("示例:")
    print("E → E+T | T")
    print("T → T*F | F")
    print("F → (E) | i")
    print("=" * 60)
    
    grammar_lines = []
    while True:
        line = input("> ")
        if not line:
            break
        grammar_lines.append(line)
    
    if not grammar_lines:
        print("使用默认文法示例...")
        grammar_text = """
        E → E+T | E-T | T
        T → T*F | T/F | F
        F → (E) | i
        """
    else:
        grammar_text = "\n".join(grammar_lines)
    
    if parser.parse_grammar(grammar_text):
        parser.compute_first_sets()
        parser.compute_follow_sets()
        
        action, goto = parser.generate_lr_tables()
        
        print("\n生成的ACTION表和GOTO表可以在LR1Parser类中使用。")
        print("注意: 由于自动生成LR分析表非常复杂，建议对复杂文法使用专业工具生成。")

if __name__ == "__main__":
    main() 