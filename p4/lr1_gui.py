#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# LR(1)分析器可视化界面

import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QTextEdit, QTableWidget, QTableWidgetItem, 
                            QTabWidget, QGridLayout, QGroupBox, QRadioButton,
                            QMessageBox, QFileDialog, QListWidget, QSplitter)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon

from lr1_parser import LR1Parser
import os

class LR1AnalyzerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 初始化解析器
        self.parser = LR1Parser()
        
        # 窗口设置
        self.setWindowTitle("LR(1)语法分析器")
        self.setGeometry(100, 100, 1000, 800)
        
        # 创建中央组件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # 创建主布局
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # 创建选项卡
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)
        
        # 创建各个选项卡页面
        self.create_analyzer_tab()
        self.create_batch_test_tab()
        self.create_grammar_tab()
        self.create_action_tab()
        self.create_about_tab()
        
        # 显示窗口
        self.show()
    
    def create_analyzer_tab(self):
        """创建分析器选项卡"""
        analyzer_tab = QWidget()
        layout = QVBoxLayout(analyzer_tab)
        
        # 创建输入区域
        input_group = QGroupBox("输入")
        input_layout = QVBoxLayout()
        
        # 输入说明
        input_label = QLabel("请输入以#结束的符号串(包括+−*/()i#):")
        input_layout.addWidget(input_label)
        
        # 输入框和分析按钮
        input_row = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("例如: i+i*i#")
        analyze_button = QPushButton("分析")
        analyze_button.clicked.connect(self.analyze_input)
        clear_button = QPushButton("清空")
        clear_button.clicked.connect(self.clear_analysis)
        
        input_row.addWidget(self.input_field)
        input_row.addWidget(analyze_button)
        input_row.addWidget(clear_button)
        input_layout.addLayout(input_row)
        
        # 示例选择
        examples_layout = QHBoxLayout()
        examples_label = QLabel("示例:")
        examples_layout.addWidget(examples_label)
        
        # 添加一些预设示例
        examples = ["i#", "i+i#", "i*i#", "i+i*i#", "(i)#", "(i+i)*i#"]
        for example in examples:
            example_button = QPushButton(example)
            example_button.clicked.connect(lambda checked, e=example: self.set_example(e))
            examples_layout.addWidget(example_button)
        
        examples_layout.addStretch()
        input_layout.addLayout(examples_layout)
        
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # 创建分析结果表格
        result_group = QGroupBox("分析过程")
        result_layout = QVBoxLayout()
        
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(5)
        self.result_table.setHorizontalHeaderLabels(["步骤", "状态栈", "符号栈", "剩余输入串", "动作"])
        self.result_table.horizontalHeader().setStretchLastSection(True)
        self.result_table.setColumnWidth(0, 50)  # 步骤列宽度
        self.result_table.setColumnWidth(1, 200)  # 状态栈列宽度
        self.result_table.setColumnWidth(2, 200)  # 符号栈列宽度
        self.result_table.setColumnWidth(3, 200)  # 剩余输入串列宽度
        
        result_layout.addWidget(self.result_table)
        
        # 结果标签
        self.result_label = QLabel("")
        result_layout.addWidget(self.result_label)
        
        result_group.setLayout(result_layout)
        layout.addWidget(result_group)
        
        # 添加选项卡
        self.tabs.addTab(analyzer_tab, "分析器")
    
    def create_batch_test_tab(self):
        """创建批量测试选项卡"""
        batch_tab = QWidget()
        layout = QVBoxLayout(batch_tab)
        
        # 创建测试文件加载区域
        file_group = QGroupBox("测试文件")
        file_layout = QHBoxLayout()
        
        # 文件路径显示
        self.test_file_path = QLineEdit()
        self.test_file_path.setReadOnly(True)
        self.test_file_path.setPlaceholderText("选择测试文件或使用默认测试文件")
        self.test_file_path.setText("test_cases.txt")  # 默认测试文件
        
        # 文件选择按钮
        browse_button = QPushButton("浏览...")
        browse_button.clicked.connect(self.browse_test_file)
        
        # 加载文件按钮
        load_button = QPushButton("加载")
        load_button.clicked.connect(self.load_test_cases)
        
        file_layout.addWidget(self.test_file_path)
        file_layout.addWidget(browse_button)
        file_layout.addWidget(load_button)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # 创建测试用例列表和结果显示的分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 测试用例列表
        case_group = QGroupBox("测试用例")
        case_layout = QVBoxLayout()
        
        self.case_list = QListWidget()
        self.case_list.currentRowChanged.connect(self.show_test_case_result)
        
        case_layout.addWidget(self.case_list)
        
        # 测试控制按钮
        test_buttons = QHBoxLayout()
        
        run_all_button = QPushButton("全部测试")
        run_all_button.clicked.connect(self.run_all_tests)
        
        run_selected_button = QPushButton("测试选中")
        run_selected_button.clicked.connect(self.run_selected_test)
        
        test_buttons.addWidget(run_all_button)
        test_buttons.addWidget(run_selected_button)
        
        case_layout.addLayout(test_buttons)
        
        case_group.setLayout(case_layout)
        splitter.addWidget(case_group)
        
        # 测试结果
        result_group = QGroupBox("测试结果")
        result_layout = QVBoxLayout()
        
        self.batch_result_table = QTableWidget()
        self.batch_result_table.setColumnCount(5)
        self.batch_result_table.setHorizontalHeaderLabels(["步骤", "状态栈", "符号栈", "剩余输入串", "动作"])
        self.batch_result_table.horizontalHeader().setStretchLastSection(True)
        
        self.batch_result_label = QLabel("")
        
        result_layout.addWidget(self.batch_result_table)
        result_layout.addWidget(self.batch_result_label)
        
        result_group.setLayout(result_layout)
        splitter.addWidget(result_group)
        
        # 设置分割器的比例
        splitter.setSizes([300, 700])
        
        layout.addWidget(splitter)
        
        # 添加选项卡
        self.tabs.addTab(batch_tab, "批量测试")
        
        # 加载默认测试文件
        self.load_test_cases()
    
    def create_grammar_tab(self):
        """创建文法选项卡"""
        grammar_tab = QWidget()
        layout = QVBoxLayout(grammar_tab)
        
        # 文法说明
        grammar_group = QGroupBox("文法规则")
        grammar_layout = QVBoxLayout()
        
        grammar_text = QTextEdit()
        grammar_text.setReadOnly(True)
        grammar_text.setPlainText("""该分析器支持以下文法规则：

1. E → E+T
2. E → E-T
3. E → T
4. T → T*F
5. T → T/F
6. T → F
7. F → (E)
8. F → i

其中，E、T、F是非终结符，+、-、*、/、(、)、i是终结符
i代表标识符或数字，#代表输入结束符
"""
        )
        
        grammar_layout.addWidget(grammar_text)
        grammar_group.setLayout(grammar_layout)
        layout.addWidget(grammar_group)
        
        # 添加产生式表
        production_group = QGroupBox("产生式表")
        production_layout = QVBoxLayout()
        
        production_table = QTableWidget()
        production_table.setColumnCount(3)
        production_table.setHorizontalHeaderLabels(["序号", "左部", "右部"])
        production_table.horizontalHeader().setStretchLastSection(True)
        
        # 填充产生式表
        productions = [
            (1, "E", "E+T"),
            (2, "E", "T"),
            (3, "T", "T*F"),
            (4, "T", "F"),
            (5, "F", "(E)"),
            (6, "F", "i"),
            (7, "E", "E-T"),
            (8, "T", "T/F")
        ]
        
        production_table.setRowCount(len(productions))
        for i, (num, left, right) in enumerate(productions):
            production_table.setItem(i, 0, QTableWidgetItem(str(num)))
            production_table.setItem(i, 1, QTableWidgetItem(left))
            production_table.setItem(i, 2, QTableWidgetItem(right))
        
        production_layout.addWidget(production_table)
        production_group.setLayout(production_layout)
        layout.addWidget(production_group)
        
        # 添加选项卡
        self.tabs.addTab(grammar_tab, "文法")
    
    def create_action_tab(self):
        """创建ACTION/GOTO表选项卡"""
        action_tab = QWidget()
        layout = QGridLayout(action_tab)
        
        # ACTION表
        action_group = QGroupBox("ACTION表")
        action_layout = QVBoxLayout()
        
        self.action_table = QTableWidget()
        self.action_table.setColumnCount(8)
        self.action_table.setHorizontalHeaderLabels(["状态", "i", "+", "-", "*", "/", "(", ")", "#"])
        
        # 填充ACTION表
        states = list(range(12))  # 0-11状态
        self.action_table.setRowCount(len(states))
        
        # 从解析器获取ACTION表内容
        for i, state in enumerate(states):
            self.action_table.setItem(i, 0, QTableWidgetItem(str(state)))
            
            if state in self.parser.action:
                state_actions = self.parser.action[state]
                
                # 设置各个符号的动作
                for col, symbol in enumerate(["i", "+", "-", "*", "/", "(", ")", "#"], 1):
                    if symbol in state_actions:
                        action_type, action_value = state_actions[symbol]
                        action_text = f"{action_type}{action_value}" if action_value is not None else action_type
                        self.action_table.setItem(i, col, QTableWidgetItem(action_text))
        
        action_layout.addWidget(self.action_table)
        action_group.setLayout(action_layout)
        layout.addWidget(action_group, 0, 0)
        
        # GOTO表
        goto_group = QGroupBox("GOTO表")
        goto_layout = QVBoxLayout()
        
        self.goto_table = QTableWidget()
        self.goto_table.setColumnCount(4)
        self.goto_table.setHorizontalHeaderLabels(["状态", "E", "T", "F"])
        
        # 填充GOTO表
        self.goto_table.setRowCount(len(states))
        
        # 从解析器获取GOTO表内容
        for i, state in enumerate(states):
            self.goto_table.setItem(i, 0, QTableWidgetItem(str(state)))
            
            if state in self.parser.goto:
                state_gotos = self.parser.goto[state]
                
                # 设置各个非终结符的GOTO
                for col, symbol in enumerate(["E", "T", "F"], 1):
                    if symbol in state_gotos:
                        self.goto_table.setItem(i, col, QTableWidgetItem(str(state_gotos[symbol])))
        
        goto_layout.addWidget(self.goto_table)
        goto_group.setLayout(goto_layout)
        layout.addWidget(goto_group, 0, 1)
        
        # 添加选项卡
        self.tabs.addTab(action_tab, "分析表")
    
    def create_about_tab(self):
        """创建关于选项卡"""
        about_tab = QWidget()
        layout = QVBoxLayout(about_tab)
        
        about_text = QTextEdit()
        about_text.setReadOnly(True)
        about_text.setHtml("""
        <h1 style="text-align: center;">LR(1)语法分析器</h1>
        <p style="text-align: center;">基于Python实现的LR(1)语法分析器，用于分析算术表达式</p>
        <hr/>
        <h2>程序结构</h2>
        <p>程序由以下几个部分组成：</p>
        <ol>
            <li>ACTION表：定义对当前状态和输入符号的动作</li>
            <li>GOTO表：定义状态转换</li>
            <li>产生式表：定义文法产生式</li>
            <li>分析算法：实现LR(1)分析过程</li>
        </ol>
        <h2>使用说明</h2>
        <p>在分析器选项卡中输入要分析的符号串，点击"分析"按钮执行分析过程。</p>
        <p>分析过程会实时显示在表格中，包括每一步的状态栈、符号栈、剩余输入串和执行的动作。</p>
        <p>注意事项：</p>
        <ul>
            <li>输入字符串必须以#结尾，表示输入结束</li>
            <li>只支持单字符的标识符i，不支持多字符标识符</li>
            <li>只支持基本的算术运算符：+、-、*、/和括号</li>
        </ul>
        <hr/>
        <p style="text-align: center;">LR(1)分析器是一种自底向上的语法分析方法，<br/>通过预先构建的分析表指导分析过程</p>
        """)
        
        layout.addWidget(about_text)
        
        # 添加选项卡
        self.tabs.addTab(about_tab, "关于")
    
    def set_example(self, example):
        """设置示例输入"""
        self.input_field.setText(example)
    
    def browse_test_file(self):
        """浏览选择测试文件"""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择测试文件", "", "文本文件 (*.txt);;所有文件 (*)")
        if file_path:
            self.test_file_path.setText(file_path)
            self.load_test_cases()
    
    def load_test_cases(self):
        """加载测试用例"""
        file_path = self.test_file_path.text()
        
        try:
            with open(file_path, 'r') as f:
                test_cases = f.readlines()
        except:
            QMessageBox.warning(self, "错误", f"无法打开文件: {file_path}")
            return
        
        # 清空列表并添加测试用例
        self.case_list.clear()
        self.test_cases = []
        
        for line in test_cases:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            self.test_cases.append(line)
            self.case_list.addItem(line)
    
    def show_test_case_result(self, row):
        """显示选中测试用例的结果"""
        if row < 0 or row >= len(self.test_cases):
            return
        
        # 清除之前的结果
        self.batch_result_table.setRowCount(0)
        self.batch_result_label.setText("")
        
        # 执行分析
        self.analyze_string(self.test_cases[row], self.batch_result_table, self.batch_result_label)
    
    def run_selected_test(self):
        """运行选中的测试用例"""
        current_row = self.case_list.currentRow()
        if current_row >= 0:
            self.show_test_case_result(current_row)
    
    def run_all_tests(self):
        """运行所有测试用例"""
        # 清除之前的所有标记
        for i in range(self.case_list.count()):
            item = self.case_list.item(i)
            item.setText(self.test_cases[i])
        
        # 检查并运行每个测试用例
        success_count = 0
        for i, test_case in enumerate(self.test_cases):
            result = self.analyze_string_silent(test_case)
            
            # 更新列表项显示
            item = self.case_list.item(i)
            if result:
                item.setText(f"✓ {test_case}")
                success_count += 1
            else:
                item.setText(f"✗ {test_case}")
        
        # 显示总结果
        total = len(self.test_cases)
        QMessageBox.information(self, "测试结果", 
                               f"测试完成！\n成功: {success_count}/{total}\n失败: {total-success_count}/{total}")
    
    def analyze_string_silent(self, input_string):
        """静默分析字符串，只返回结果不显示"""
        if not input_string.endswith('#'):
            input_string += '#'
            
        # 使用解析器分析，但不显示结果
        return self.parser.parse(input_string, silent=True)
    
    def analyze_input(self):
        """分析输入框中的符号串"""
        input_string = self.input_field.text()
        
        # 检查输入是否合法
        valid_chars = set('i+-*/()#')
        if not all(char in valid_chars for char in input_string):
            QMessageBox.warning(self, "输入错误", "输入包含不支持的字符。请只使用i, +, -, *, /, (, ), #")
            return
        
        # 确保输入以#结尾
        if not input_string.endswith('#'):
            input_string += '#'
            self.input_field.setText(input_string)
        
        # 清空结果
        self.result_table.setRowCount(0)
        self.result_label.setText("")
        
        # 执行分析
        self.analyze_string(input_string, self.result_table, self.result_label)
    
    def analyze_string(self, input_string, result_table, result_label):
        """分析符号串并显示结果到指定表格和标签"""
        # 初始化分析过程的变量
        state_stack = [0]  # 状态栈初始状态为0
        symbol_stack = ['#']  # 符号栈初始符号为#
        input_chars = list(input_string)
        current_pos = 0
        current_char = input_chars[current_pos]
        
        # 清空表格
        result_table.setRowCount(0)
        result_label.setText("")
        
        step = 1
        while True:
            # 获取当前状态栈顶的状态
            current_state = state_stack[-1]
            
            # 当前分析步骤信息
            state_str = ''.join(map(str, state_stack))
            symbol_str = ''.join(symbol_stack)
            input_str = ''.join(input_chars[current_pos:])
            
            # 插入新行到结果表格
            row = result_table.rowCount()
            result_table.insertRow(row)
            
            # 检查当前状态和输入符号的动作
            if current_state in self.parser.action and current_char in self.parser.action[current_state]:
                action_type, action_value = self.parser.action[current_state][current_char]
                
                # 设置表格数据
                result_table.setItem(row, 0, QTableWidgetItem(str(step)))
                result_table.setItem(row, 1, QTableWidgetItem(state_str))
                result_table.setItem(row, 2, QTableWidgetItem(symbol_str))
                result_table.setItem(row, 3, QTableWidgetItem(input_str))
                
                # 根据动作类型执行相应操作
                if action_type == 'S':  # 移进
                    result_table.setItem(row, 4, QTableWidgetItem("移进"))
                    state_stack.append(action_value)
                    symbol_stack.append(current_char)
                    current_pos += 1
                    current_char = input_chars[current_pos]
                    
                elif action_type == 'r':  # 归约
                    production_num = action_value
                    left, right = self.parser.productions[production_num]
                    
                    action_text = f"r{production_num}: {left}→{right}归约"
                    result_table.setItem(row, 4, QTableWidgetItem(action_text))
                    
                    # 弹出|β|个符号和状态
                    for _ in range(len(right)):
                        state_stack.pop()
                        symbol_stack.pop()
                    
                    # 当前状态
                    current_state = state_stack[-1]
                    
                    # 压入左部非终结符
                    symbol_stack.append(left)
                    
                    # 查找GOTO表，获取新状态
                    if current_state in self.parser.goto and left in self.parser.goto[current_state]:
                        new_state = self.parser.goto[current_state][left]
                        state_stack.append(new_state)
                    else:
                        error_msg = f"错误：无法找到GOTO[{current_state},{left}]"
                        result_label.setText(error_msg)
                        result_label.setStyleSheet("color: red;")
                        return False
                    
                elif action_type == 'acc':  # 接受
                    result_table.setItem(row, 4, QTableWidgetItem("接受"))
                    result_label.setText("分析成功！")
                    result_label.setStyleSheet("color: green; font-weight: bold;")
                    return True
            else:
                # 错误处理
                result_table.setItem(row, 0, QTableWidgetItem(str(step)))
                result_table.setItem(row, 1, QTableWidgetItem(state_str))
                result_table.setItem(row, 2, QTableWidgetItem(symbol_str))
                result_table.setItem(row, 3, QTableWidgetItem(input_str))
                result_table.setItem(row, 4, QTableWidgetItem("错误"))
                
                error_msg = f"错误：状态{current_state}下遇到意外的符号'{current_char}'"
                result_label.setText(error_msg)
                result_label.setStyleSheet("color: red;")
                return False
            
            step += 1
    
    def clear_analysis(self):
        """清空分析结果"""
        self.input_field.clear()
        self.result_table.setRowCount(0)
        self.result_label.setText("")

def main():
    app = QApplication(sys.argv)
    window = LR1AnalyzerGUI()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 