#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
词法分析器
实现对C语言子集的词法分析
"""

import sys

# 单词种别码定义
TYPE_KEYWORD = 1      # 关键字
TYPE_DELIMITER = 2    # 分界符
TYPE_OPERATOR = 3     # 算术运算符
TYPE_RELATIONAL = 4   # 关系运算符
TYPE_CONSTANT = 5     # 常数
TYPE_IDENTIFIER = 6   # 标识符

# 表格定义
# 关键字表
keywords = ['do', 'end', 'for', 'if', 'printf', 'scanf', 'then', 'while', 'else']

# 分界符表
delimiters = [',', ';', '(', ')', '[', ']', '{', '}']

# 算术运算符表
operators = {
    '+': 0x10, 
    '-': 0x11, 
    '*': 0x20, 
    '/': 0x21,
    '&': 0x30  # 添加&符号作为取地址运算符
}

# 关系运算符表
relational_operators = {
    '<': 0x00,
    '<=': 0x01,
    '=': 0x02,
    '>': 0x03,
    '>=': 0x04,
    '<>': 0x05
}

# 标识符表
identifiers = []

# 常数表
constants = []

class LexicalAnalyzer:
    def __init__(self, input_file=None):
        self.input_file = input_file
        self.content = ""
        self.position = 0
        self.line = 1
        self.column = 1
        self.current_char = None
        self.tokens = []
        self.error_count = 0
        
    def load_file(self, input_file):
        """从文件中加载源代码"""
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                self.content = f.read()
            self.position = 0
            self.line = 1
            self.column = 1
            return True
        except Exception as e:
            print(f"无法打开文件: {e}")
            return False
            
    def load_string(self, content):
        """从字符串中加载源代码"""
        self.content = content
        self.position = 0
        self.line = 1
        self.column = 1
        
    def get_char(self):
        """获取当前字符并移动指针到下一个位置"""
        if self.position >= len(self.content):
            self.current_char = None
            return None
            
        self.current_char = self.content[self.position]
        self.position += 1
        
        # 更新行号和列号
        if self.current_char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
            
        return self.current_char
        
    def peek_char(self):
        """预读下一个字符，不移动指针"""
        if self.position >= len(self.content):
            return None
        return self.content[self.position]
        
    def skip_whitespace(self):
        """跳过空白字符（空格、制表符、换行符）"""
        while self.current_char is not None and self.current_char.isspace():
            self.get_char()
            
    def handle_error(self, error_msg):
        """处理错误"""
        self.error_count += 1
        return {
            'type': 'Error',
            'value': error_msg,
            'line': self.line,
            'column': self.column - 1,
            'error_msg': error_msg
        }
        
    def is_keyword(self, word):
        """检查单词是否为关键字"""
        return word in keywords
        
    def is_delimiter(self, char):
        """检查字符是否为分界符"""
        return char in delimiters
        
    def is_operator(self, char):
        """检查字符是否为算术运算符"""
        return char in operators
        
    def is_relational_operator_start(self, char):
        """检查字符是否为关系运算符的开始"""
        return char in ['<', '=', '>']
        
    def analyze(self):
        """执行词法分析，生成token序列"""
        self.get_char()  # 读取第一个字符
        
        while self.current_char is not None:
            # 跳过空白字符
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
                
            # 处理标识符和关键字
            if self.current_char.isalpha() or self.current_char == '_':
                token = self.handle_identifier()
                self.tokens.append(token)
                continue
                
            # 处理数字
            if self.current_char.isdigit():
                token = self.handle_number()
                self.tokens.append(token)
                continue
                
            # 处理分界符
            if self.is_delimiter(self.current_char):
                token = {
                    'type': TYPE_DELIMITER,
                    'value': self.current_char,
                    'line': self.line,
                    'column': self.column - 1
                }
                self.tokens.append(token)
                self.get_char()
                continue
                
            # 处理算术运算符
            if self.is_operator(self.current_char):
                # 处理特殊情况：++
                if self.current_char == '+' and self.peek_char() == '+':
                    start_column = self.column - 1
                    token = {
                        'type': 'Error',
                        'value': '++',
                        'line': self.line,
                        'column': start_column,
                        'error_msg': "非法的运算符: ++"
                    }
                    self.get_char()  # 跳过第一个+
                    self.get_char()  # 跳过第二个+
                    self.error_count += 1
                elif self.current_char == '&':
                    # 处理取地址符号
                    start_column = self.column - 1
                    token = {
                        'type': TYPE_OPERATOR,
                        'value': '&',
                        'line': self.line,
                        'column': start_column
                    }
                    self.get_char()
                else:
                    token = {
                        'type': TYPE_OPERATOR,
                        'value': self.current_char,
                        'line': self.line,
                        'column': self.column - 1
                    }
                    self.get_char()
                
                self.tokens.append(token)
                continue
                
            # 处理关系运算符
            if self.is_relational_operator_start(self.current_char):
                token = self.handle_relational_operator()
                self.tokens.append(token)
                continue
                
            # 处理字符串常量
            if self.current_char == '"':
                token = self.handle_string()
                self.tokens.append(token)
                continue
                
            # 处理特殊情况：%
            if self.current_char == '%':
                token = self.handle_error(f"非法的字符: %")
                self.tokens.append(token)
                self.get_char()
                continue
                
            # 处理未识别的字符
            error_token = self.handle_error(f"未识别的字符: {self.current_char}")
            self.tokens.append(error_token)
            self.get_char()
            
        return self.tokens
        
    def handle_string(self):
        """处理字符串常量"""
        # 保存当前位置信息
        start_line = self.line
        start_column = self.column - 1
        
        # 收集字符串字符
        lexeme = self.current_char  # 包含开始的双引号
        self.get_char()
        
        while self.current_char is not None and self.current_char != '"':
            lexeme += self.current_char
            self.get_char()
            
        if self.current_char == '"':
            lexeme += self.current_char
            self.get_char()
            
            # 将字符串常量加入常数表
            if lexeme not in constants:
                constants.append(lexeme)
                
            return {
                'type': TYPE_CONSTANT,
                'value': lexeme,
                'line': start_line,
                'column': start_column
            }
        else:
            # 未闭合的字符串
            return self.handle_error(f"未闭合的字符串常量: {lexeme}")
            
    def handle_identifier(self):
        """处理标识符和关键字"""
        # 保存当前位置信息
        start_line = self.line
        start_column = self.column - 1
        
        # 收集标识符字符
        lexeme = ""
        while (self.current_char is not None and 
               (self.current_char.isalnum() or self.current_char == '_')):
            lexeme += self.current_char
            self.get_char()
            
        # 判断是否为关键字
        if self.is_keyword(lexeme):
            return {
                'type': TYPE_KEYWORD,
                'value': lexeme,
                'line': start_line,
                'column': start_column
            }
        else:
            # 是标识符，需要登记到标识符表中
            if lexeme not in identifiers:
                identifiers.append(lexeme)
            
            return {
                'type': TYPE_IDENTIFIER,
                'value': lexeme,
                'line': start_line,
                'column': start_column
            }
            
    def handle_number(self):
        """处理数字常量"""
        # 保存当前位置信息
        start_line = self.line
        start_column = self.column - 1
        
        # 收集数字字符
        lexeme = ""
        is_valid = True
        
        # 处理整数部分
        while self.current_char is not None and self.current_char.isdigit():
            lexeme += self.current_char
            self.get_char()
            
        # 处理小数部分
        if self.current_char == '.':
            lexeme += self.current_char
            self.get_char()
            
            # 小数点后必须有数字
            if not (self.current_char is not None and self.current_char.isdigit()):
                is_valid = False
                
            while self.current_char is not None and self.current_char.isdigit():
                lexeme += self.current_char
                self.get_char()
                
        # 检查数字后面是否有字母，如果有则是非法的
        if (self.current_char is not None and 
            (self.current_char.isalpha() or self.current_char == '_')):
            is_valid = False
            error_lexeme = lexeme + self.current_char
            while (self.current_char is not None and 
                  (self.current_char.isalnum() or self.current_char == '_')):
                error_lexeme += self.current_char
                self.get_char()
                
            return self.handle_error(f"非法的数字常量: {error_lexeme}")
            
        if not is_valid:
            return self.handle_error(f"非法的数字常量: {lexeme}")
            
        # 将常数加入常数表
        if lexeme not in constants:
            constants.append(lexeme)
            
        return {
            'type': TYPE_CONSTANT,
            'value': lexeme,
            'line': start_line,
            'column': start_column
        }
        
    def handle_relational_operator(self):
        """处理关系运算符"""
        # 保存当前位置信息
        start_line = self.line
        start_column = self.column - 1
        
        first_char = self.current_char
        self.get_char()  # 移动到下一个字符
        
        # 检查双字符运算符
        if first_char == '<' and self.current_char == '=':
            self.get_char()  # 移动到下一个字符
            return {
                'type': TYPE_RELATIONAL,
                'value': '<=',
                'line': start_line,
                'column': start_column
            }
        elif first_char == '>' and self.current_char == '=':
            self.get_char()  # 移动到下一个字符
            return {
                'type': TYPE_RELATIONAL,
                'value': '>=',
                'line': start_line,
                'column': start_column
            }
        elif first_char == '<' and self.current_char == '>':
            self.get_char()  # 移动到下一个字符
            return {
                'type': TYPE_RELATIONAL,
                'value': '<>',
                'line': start_line,
                'column': start_column
            }
        else:
            # 单字符运算符
            op = first_char
            if op in relational_operators:
                return {
                    'type': TYPE_RELATIONAL,
                    'value': op,
                    'line': start_line,
                    'column': start_column
                }
            else:
                return self.handle_error(f"非法的关系运算符: {op}")
                
    def get_type_name(self, type_code):
        """获取类型名称"""
        type_names = {
            TYPE_KEYWORD: "关键字",
            TYPE_DELIMITER: "分界符",
            TYPE_OPERATOR: "算术运算符",
            TYPE_RELATIONAL: "关系运算符",
            TYPE_CONSTANT: "常数",
            TYPE_IDENTIFIER: "标识符",
            "Error": "Error"
        }
        return type_names.get(type_code, "未知类型")
        
    def get_token_attribute(self, token):
        """获取token的属性值"""
        if token['type'] == TYPE_KEYWORD:
            return keywords.index(token['value'])
        elif token['type'] == TYPE_DELIMITER:
            return delimiters.index(token['value'])
        elif token['type'] == TYPE_OPERATOR:
            return operators.get(token['value'], 0)
        elif token['type'] == TYPE_RELATIONAL:
            return relational_operators.get(token['value'], 0)
        elif token['type'] == TYPE_CONSTANT:
            return constants.index(token['value'])
        elif token['type'] == TYPE_IDENTIFIER:
            return identifiers.index(token['value'])
        else:
            return "Error"
            
    def print_results(self):
        """打印词法分析结果"""
        print(f"{'单词':<15}{'二元序列':<25}{'类型':<15}{'位置（行，列）':<15}")
        print("-" * 70)
        
        for token in self.tokens:
            if token['type'] == 'Error':
                type_name = "Error"
                attribute = "Error"
                print(f"{token['value']:<15}({type_name},{attribute}){' ':<10}{type_name:<15}({token['line']}, {token['column']})")
            else:
                type_name = self.get_type_name(token['type'])
                attribute = token['value']
                print(f"{token['value']:<15}({token['type']},{attribute}){' ':<10}{type_name:<15}({token['line']}, {token['column']})")

def main():
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("用法: python lexical_analyzer.py <输入文件>")
        return
        
    input_file = sys.argv[1]
    analyzer = LexicalAnalyzer()
    
    # 加载文件
    if not analyzer.load_file(input_file):
        return
        
    # 执行词法分析
    tokens = analyzer.analyze()
    
    # 打印结果
    analyzer.print_results()
    
    # 打印统计信息
    print("\n分析统计:")
    print(f"标识符表: {identifiers}")
    print(f"常数表: {constants}")
    print(f"错误数量: {analyzer.error_count}")

if __name__ == "__main__":
    main() 