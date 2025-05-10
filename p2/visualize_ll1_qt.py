#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import io
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QLineEdit, QPushButton, QTextEdit, QTabWidget,
                            QTreeWidget, QTreeWidgetItem, QFrame, QSplitter, QTableWidget,
                            QTableWidgetItem, QHeaderView, QMessageBox, QGroupBox, QSizePolicy)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont
from ll1_parser import LL1Parser

class LL1VisualizerQt(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 创建解析器实例
        self.parser = LL1Parser()
        
        # 设置窗口属性
        self.setWindowTitle("LL(1)语法分析可视化工具")
        self.setGeometry(100, 100, 1000, 800)
        
        # 创建UI界面
        self.init_ui()
        
        # 显示First集和Follow集
        self.show_sets_dialog()
    
    def init_ui(self):
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建文法显示区
        grammar_group = QGroupBox("文法规则")
        grammar_layout = QVBoxLayout(grammar_group)
        
        grammar_text = QTextEdit()
        grammar_text.setReadOnly(True)
        # 使用系统默认等宽字体，避免字体警告
        grammar_text.setFont(QFont("Menlo, Monaco, Courier New, monospace", 10))
        grammar_text.setText("E -> TG\n"
                           "G -> +TG | -TG | ε\n"
                           "T -> FS\n"
                           "S -> *FS | /FS | ε\n"
                           "F -> (E) | i")
        grammar_layout.addWidget(grammar_text)
        
        # 创建输入区
        input_group = QGroupBox("输入表达式")
        input_layout = QHBoxLayout(input_group)
        
        self.input_edit = QLineEdit()
        input_layout.addWidget(self.input_edit)
        
        analyze_btn = QPushButton("分析")
        analyze_btn.clicked.connect(self.analyze)
        input_layout.addWidget(analyze_btn)
        
        clear_btn = QPushButton("清空")
        clear_btn.clicked.connect(self.clear)
        input_layout.addWidget(clear_btn)
        
        # 创建分析结果区
        result_group = QGroupBox("分析过程")
        result_layout = QVBoxLayout(result_group)
        
        # 创建表格显示分析过程
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(5)
        self.result_table.setHorizontalHeaderLabels(["步骤", "分析栈", "剩余输入串", "所用产生式", "动作"])
        
        # 设置列宽
        self.result_table.setColumnWidth(0, 60)
        self.result_table.setColumnWidth(1, 160)
        self.result_table.setColumnWidth(2, 160)
        self.result_table.setColumnWidth(3, 200)
        self.result_table.setColumnWidth(4, 200)
        
        # 允许表格自动调整大小
        self.result_table.horizontalHeader().setStretchLastSection(True)
        
        result_layout.addWidget(self.result_table)
        
        # 创建状态栏
        self.statusBar().showMessage("准备就绪")
        
        # 添加所有组件到主布局
        main_layout.addWidget(grammar_group)
        main_layout.addWidget(input_group)
        main_layout.addWidget(result_group)
        
        # 设置布局比例
        main_layout.setStretch(0, 2)  # 文法区
        main_layout.setStretch(1, 1)  # 输入区
        main_layout.setStretch(2, 5)  # 结果区

    def show_sets_dialog(self):
        # 创建对话框窗口
        self.sets_dialog = QWidget()
        self.sets_dialog.setWindowTitle("First集和Follow集")
        self.sets_dialog.setGeometry(200, 200, 600, 500)
        
        dialog_layout = QVBoxLayout(self.sets_dialog)
        
        # 创建选项卡部件
        tab_widget = QTabWidget()
        
        # First集选项卡
        first_tab = QWidget()
        first_layout = QVBoxLayout(first_tab)
        
        first_text = QTextEdit()
        first_text.setReadOnly(True)
        first_text.setFont(QFont("Menlo, Monaco, Courier New, monospace", 10))
        
        for nt in self.parser.non_terminals:
            first_text.append(f"FIRST({nt}) = {{{', '.join(sorted(self.parser.first[nt]))}}}")
        
        first_layout.addWidget(first_text)
        tab_widget.addTab(first_tab, "First集")
        
        # Follow集选项卡
        follow_tab = QWidget()
        follow_layout = QVBoxLayout(follow_tab)
        
        follow_text = QTextEdit()
        follow_text.setReadOnly(True)
        follow_text.setFont(QFont("Menlo, Monaco, Courier New, monospace", 10))
        
        for nt in self.parser.non_terminals:
            follow_text.append(f"FOLLOW({nt}) = {{{', '.join(sorted(self.parser.follow[nt]))}}}")
        
        follow_layout.addWidget(follow_text)
        tab_widget.addTab(follow_tab, "Follow集")
        
        # 分析表选项卡
        table_tab = QWidget()
        table_layout = QVBoxLayout(table_tab)
        
        # 创建分析表网格
        table_widget = QTableWidget()
        table_widget.setColumnCount(len(self.parser.terminals) + 1)
        table_widget.setRowCount(len(self.parser.non_terminals))
        
        # 设置水平表头
        headers = ["非终结符"] + self.parser.terminals
        table_widget.setHorizontalHeaderLabels(headers)
        
        # 设置垂直表头
        table_widget.setVerticalHeaderLabels(self.parser.non_terminals)
        
        # 填充表格数据
        for i, nt in enumerate(self.parser.non_terminals):
            # 设置非终结符列
            nt_item = QTableWidgetItem(nt)
            nt_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table_widget.setItem(i, 0, nt_item)
            
            # 设置各终结符对应的产生式
            for j, t in enumerate(self.parser.terminals):
                if self.parser.table[nt][t] is not None:
                    production = self.parser.table[nt][t]
                    production_str = f"{nt} -> {''.join(production)}"
                    item = QTableWidgetItem(production_str)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    table_widget.setItem(i, j + 1, item)
                else:
                    table_widget.setItem(i, j + 1, QTableWidgetItem(""))
        
        # 调整列宽自适应内容
        table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        
        table_layout.addWidget(table_widget)
        tab_widget.addTab(table_tab, "分析表")
        
        dialog_layout.addWidget(tab_widget)
        
        self.sets_dialog.show()

    def analyze(self):
        # 获取输入表达式
        input_string = self.input_edit.text().strip()
        
        if not input_string:
            QMessageBox.warning(self, "警告", "请输入表达式！")
            return
        
        # 清空结果表格
        self.result_table.setRowCount(0)
        
        # 创建自定义的分析函数来捕获结果，避免使用标准输出重定向
        results = self.run_parser(input_string)
        
        # 处理分析结果并显示在表格中
        for step, stack, remain, production, action in results:
            row_position = self.result_table.rowCount()
            self.result_table.insertRow(row_position)
            
            # 创建表格项并设置内容
            self.result_table.setItem(row_position, 0, QTableWidgetItem(str(step)))
            self.result_table.setItem(row_position, 1, QTableWidgetItem(str(stack)))
            self.result_table.setItem(row_position, 2, QTableWidgetItem(str(remain)))
            self.result_table.setItem(row_position, 3, QTableWidgetItem(str(production)))
            self.result_table.setItem(row_position, 4, QTableWidgetItem(str(action)))
        
        # 自动调整行高以适应内容
        self.result_table.resizeRowsToContents()
        
        # 更新状态栏
        if results and results[-1][4] == "成功":
            self.statusBar().showMessage("分析成功！")
        else:
            self.statusBar().showMessage("分析失败！")

    def run_parser(self, input_string):
        """自定义分析函数，直接返回分析步骤结果，避免使用标准输出重定向"""
        # 初始化结果列表
        results = []
        
        # 添加终止符
        full_input = input_string + '#'
        stack = ['#', 'E']  # 初始化栈，包含起始符号E和栈底标记#
        
        # 添加初始状态
        results.append((0, stack.copy(), full_input, "初始化", "初始化"))
        
        # 当前输入符号的索引
        index = 0
        step = 0
        
        while stack:
            step += 1
            
            # 获取栈顶元素和当前输入符号
            top = stack[-1]
            current_input = full_input[index]
            
            # 如果栈顶是终结符或#
            if top in self.parser.terminals or top == '#':
                if top == current_input:  # 匹配成功
                    stack.pop()
                    action = "POP"
                    production = f"匹配 {top}"
                    index += 1
                    results.append((step, stack.copy(), full_input[index:], production, action))
                else:  # 匹配失败
                    error_msg = f"错误：栈顶终结符 {top} 与当前输入 {current_input} 不匹配"
                    results.append((step, stack.copy(), full_input[index:], error_msg, "错误"))
                    return results
            
            # 如果栈顶是非终结符
            elif top in self.parser.non_terminals:
                if self.parser.table[top][current_input] is not None:  # 有对应的产生式
                    production = self.parser.table[top][current_input]
                    stack.pop()
                    
                    # 准备产生式字符串
                    production_str = f"{top} -> {''.join(production)}"
                    
                    # 如果产生式不是空串，则逆序入栈
                    pushed_symbols = []
                    if production != ['ε']:
                        for symbol in reversed(production):
                            stack.append(symbol)
                            pushed_symbols.append(symbol)
                    
                    # 准备动作字符串
                    if pushed_symbols:
                        action = f"POP, PUSH({', '.join(reversed(pushed_symbols))})"
                    else:
                        action = "POP"
                    
                    results.append((step, stack.copy(), full_input[index:], production_str, action))
                else:  # 没有对应的产生式
                    error_msg = f"错误：分析表中没有 [{top}, {current_input}] 对应的产生式"
                    results.append((step, stack.copy(), full_input[index:], error_msg, "错误"))
                    return results
            else:
                error_msg = f"错误：未知的栈顶符号 {top}"
                results.append((step, stack.copy(), full_input[index:], error_msg, "错误"))
                return results
            
            # 如果栈为空但输入未结束，或者栈不为空但输入已结束，则分析失败
            if (not stack and index < len(full_input) - 1) or (stack and index >= len(full_input)):
                error_msg = "错误：分析提前结束或输入不完整"
                results.append((step, stack.copy(), full_input[index:], error_msg, "错误"))
                return results
            
            # 如果栈顶和输入都是#，则分析成功
            if stack and index < len(full_input) and stack[-1] == '#' and full_input[index] == '#':
                results.append((step, stack.copy(), full_input[index:], "接受", "成功"))
                return results
        
        return results

    def clear(self):
        # 清空输入和结果
        self.input_edit.clear()
        self.result_table.setRowCount(0)
        self.statusBar().showMessage("准备就绪")


def main():
    app = QApplication(sys.argv)
    window = LL1VisualizerQt()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 