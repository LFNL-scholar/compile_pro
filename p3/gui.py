#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QLineEdit, QPushButton, QTextEdit, QTabWidget,
                           QTableWidget, QTableWidgetItem, QGroupBox, QGridLayout, QSpinBox,
                           QMessageBox, QSplitter, QFrame, QHeaderView)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon

from infix_to_postfix import InfixToPostfix
from postfix_calculator import PostfixCalculator
from debug_process import DebugProcess

class RPNCalculatorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.infix_converter = InfixToPostfix()
        self.calculator = PostfixCalculator()
        self.debugger = DebugProcess()
        self.variables = {}  # 存储变量值
        
        self.init_ui()
        
    def init_ui(self):
        # 设置窗口属性
        self.setWindowTitle('逆波兰表达式计算器')
        self.setGeometry(100, 100, 1000, 800)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建标题标签
        title_label = QLabel('逆波兰表达式转换与计算')
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont('Arial', 16, QFont.Weight.Bold)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)
        
        # 创建选项卡部件
        tab_widget = QTabWidget()
        
        # 创建"转换"选项卡
        conversion_tab = QWidget()
        tab_widget.addTab(conversion_tab, "表达式转换")
        
        # 创建"计算"选项卡
        calculation_tab = QWidget()
        tab_widget.addTab(calculation_tab, "表达式计算")
        
        # 创建"步骤调试"选项卡
        debug_tab = QWidget()
        tab_widget.addTab(debug_tab, "步骤调试")
        
        # 添加选项卡部件到主布局
        main_layout.addWidget(tab_widget)
        
        # 设置"转换"选项卡的布局
        self.setup_conversion_tab(conversion_tab)
        
        # 设置"计算"选项卡的布局
        self.setup_calculation_tab(calculation_tab)
        
        # 设置"步骤调试"选项卡的布局
        self.setup_debug_tab(debug_tab)
        
    def setup_conversion_tab(self, tab):
        # 创建布局
        layout = QVBoxLayout(tab)
        
        # 创建输入部分
        input_group = QGroupBox("中缀表达式输入")
        input_layout = QHBoxLayout()
        
        self.infix_input = QLineEdit()
        self.infix_input.setPlaceholderText("请输入中缀表达式 (如: (a+b*c)*d#)")
        input_layout.addWidget(self.infix_input)
        
        convert_button = QPushButton("转换")
        convert_button.clicked.connect(self.convert_expression)
        input_layout.addWidget(convert_button)
        
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # 创建结果部分
        result_group = QGroupBox("转换结果")
        result_layout = QVBoxLayout()
        
        self.conversion_result = QTextEdit()
        self.conversion_result.setReadOnly(True)
        result_layout.addWidget(self.conversion_result)
        
        result_group.setLayout(result_layout)
        layout.addWidget(result_group)
        
    def setup_calculation_tab(self, tab):
        # 创建布局
        layout = QVBoxLayout(tab)
        
        # 创建输入部分
        input_group = QGroupBox("表达式输入")
        input_layout = QVBoxLayout()
        
        infix_layout = QHBoxLayout()
        infix_label = QLabel("中缀表达式:")
        infix_layout.addWidget(infix_label)
        
        self.calc_infix_input = QLineEdit()
        self.calc_infix_input.setPlaceholderText("请输入中缀表达式 (如: (a+b*c)*d#)")
        infix_layout.addWidget(self.calc_infix_input)
        
        input_layout.addLayout(infix_layout)
        
        # 后缀表达式显示
        postfix_layout = QHBoxLayout()
        postfix_label = QLabel("后缀表达式:")
        postfix_layout.addWidget(postfix_label)
        
        self.calc_postfix_display = QLineEdit()
        self.calc_postfix_display.setReadOnly(True)
        postfix_layout.addWidget(self.calc_postfix_display)
        
        input_layout.addLayout(postfix_layout)
        
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # 创建变量输入部分
        var_group = QGroupBox("变量赋值")
        var_layout = QGridLayout()
        
        # 创建4x2的变量输入网格
        var_labels = []
        self.var_inputs = []
        
        for i in range(4):
            for j in range(2):
                idx = i * 2 + j
                var_name = chr(97 + idx)  # 从'a'开始的变量名
                
                label = QLabel(f"{var_name} = ")
                var_layout.addWidget(label, i, j*2)
                var_labels.append(label)
                
                var_input = QLineEdit()
                var_input.setPlaceholderText("数值")
                var_layout.addWidget(var_input, i, j*2+1)
                self.var_inputs.append(var_input)
        
        var_group.setLayout(var_layout)
        layout.addWidget(var_group)
        
        # 创建操作按钮
        button_layout = QHBoxLayout()
        
        convert_calc_button = QPushButton("转换")
        convert_calc_button.clicked.connect(self.calculate_convert)
        button_layout.addWidget(convert_calc_button)
        
        calculate_button = QPushButton("计算")
        calculate_button.clicked.connect(self.calculate_expression)
        button_layout.addWidget(calculate_button)
        
        clear_button = QPushButton("清除")
        clear_button.clicked.connect(self.clear_calculation)
        button_layout.addWidget(clear_button)
        
        layout.addLayout(button_layout)
        
        # 创建结果部分
        result_group = QGroupBox("计算结果")
        result_layout = QVBoxLayout()
        
        self.calculation_result = QTextEdit()
        self.calculation_result.setReadOnly(True)
        result_layout.addWidget(self.calculation_result)
        
        result_group.setLayout(result_layout)
        layout.addWidget(result_group)
    
    def setup_debug_tab(self, tab):
        # 创建布局
        layout = QVBoxLayout(tab)
        
        # 创建输入部分
        input_group = QGroupBox("表达式输入")
        input_layout = QVBoxLayout()
        
        infix_layout = QHBoxLayout()
        infix_label = QLabel("中缀表达式:")
        infix_layout.addWidget(infix_label)
        
        self.debug_infix_input = QLineEdit()
        self.debug_infix_input.setPlaceholderText("请输入中缀表达式 (如: (a+b*c)*d#)")
        infix_layout.addWidget(self.debug_infix_input)
        
        debug_button = QPushButton("调试")
        debug_button.clicked.connect(self.debug_process)
        infix_layout.addWidget(debug_button)
        
        input_layout.addLayout(infix_layout)
        
        # 变量输入
        var_layout = QHBoxLayout()
        var_label = QLabel("变量赋值:")
        var_layout.addWidget(var_label)
        
        self.debug_var_input = QLineEdit()
        self.debug_var_input.setPlaceholderText("请输入变量赋值 (如: a=2;b=3;c=4;d=5)")
        var_layout.addWidget(self.debug_var_input)
        
        input_layout.addLayout(var_layout)
        
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # 创建表格显示部分
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # 创建中缀到后缀的过程表
        infix_to_postfix_group = QGroupBox("中缀表达式转后缀表达式过程")
        infix_to_postfix_layout = QVBoxLayout()
        
        self.infix_to_postfix_table = QTableWidget()
        self.infix_to_postfix_table.setColumnCount(5)
        self.infix_to_postfix_table.setHorizontalHeaderLabels(['步骤', '当前符号', '输入区', '运算符栈', '输出区'])
        self.infix_to_postfix_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        infix_to_postfix_layout.addWidget(self.infix_to_postfix_table)
        infix_to_postfix_group.setLayout(infix_to_postfix_layout)
        
        splitter.addWidget(infix_to_postfix_group)
        
        # 创建后缀表达式计算过程表
        postfix_eval_group = QGroupBox("后缀表达式计算过程")
        postfix_eval_layout = QVBoxLayout()
        
        self.postfix_eval_table = QTableWidget()
        self.postfix_eval_table.setColumnCount(4)
        self.postfix_eval_table.setHorizontalHeaderLabels(['步骤', '当前符号', '栈内容', '说明'])
        self.postfix_eval_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        postfix_eval_layout.addWidget(self.postfix_eval_table)
        postfix_eval_group.setLayout(postfix_eval_layout)
        
        splitter.addWidget(postfix_eval_group)
        
        layout.addWidget(splitter)
        
        # 创建结果显示
        result_layout = QHBoxLayout()
        result_label = QLabel("计算结果:")
        result_layout.addWidget(result_label)
        
        self.debug_result = QLineEdit()
        self.debug_result.setReadOnly(True)
        result_layout.addWidget(self.debug_result)
        
        layout.addLayout(result_layout)
    
    # 表达式转换功能
    def convert_expression(self):
        infix_expr = self.infix_input.text().strip()
        if not infix_expr:
            QMessageBox.warning(self, "输入错误", "请输入中缀表达式")
            return
            
        try:
            # 确保表达式以#结尾
            if not infix_expr.endswith('#'):
                infix_expr += '#'
                
            postfix_expr = self.infix_converter.infix_to_postfix(infix_expr)
            self.conversion_result.setText(f"中缀表达式: {infix_expr}\n\n后缀表达式: {postfix_expr}")
            
        except Exception as e:
            QMessageBox.critical(self, "转换错误", f"转换过程中发生错误: {e}")
    
    # 计算选项卡的转换功能
    def calculate_convert(self):
        infix_expr = self.calc_infix_input.text().strip()
        if not infix_expr:
            QMessageBox.warning(self, "输入错误", "请输入中缀表达式")
            return
            
        try:
            # 确保表达式以#结尾
            if not infix_expr.endswith('#'):
                infix_expr += '#'
                
            postfix_expr = self.infix_converter.infix_to_postfix(infix_expr)
            self.calc_postfix_display.setText(postfix_expr)
            
        except Exception as e:
            QMessageBox.critical(self, "转换错误", f"转换过程中发生错误: {e}")
    
    # 计算表达式功能
    def calculate_expression(self):
        infix_expr = self.calc_infix_input.text().strip()
        if not infix_expr:
            QMessageBox.warning(self, "输入错误", "请输入中缀表达式")
            return
            
        try:
            # 确保表达式以#结尾
            if not infix_expr.endswith('#'):
                infix_expr += '#'
                
            # 如果没有先转换，则先进行转换
            if not self.calc_postfix_display.text():
                postfix_expr = self.infix_converter.infix_to_postfix(infix_expr)
                self.calc_postfix_display.setText(postfix_expr)
            else:
                postfix_expr = self.calc_postfix_display.text()
            
            # 获取变量值
            variables = {}
            for i, var_input in enumerate(self.var_inputs):
                var_text = var_input.text().strip()
                if var_text:
                    var_name = chr(97 + i)  # 从'a'开始的变量名
                    try:
                        var_value = float(var_text)
                        variables[var_name] = var_value
                        self.calculator.set_variable(var_name, var_value)
                    except ValueError:
                        QMessageBox.warning(self, "输入错误", f"变量 {var_name} 的值必须是数字")
                        return
            
            # 计算结果
            result = self.calculator.evaluate_postfix(postfix_expr)
            
            # 显示结果
            output = f"中缀表达式: {infix_expr}\n\n后缀表达式: {postfix_expr}\n\n变量赋值:\n"
            for name, value in variables.items():
                output += f"  {name} = {value}\n"
            output += f"\n计算结果: {result}"
            
            self.calculation_result.setText(output)
            
        except Exception as e:
            QMessageBox.critical(self, "计算错误", f"计算过程中发生错误: {e}")
    
    # 清除计算面板
    def clear_calculation(self):
        self.calc_infix_input.clear()
        self.calc_postfix_display.clear()
        self.calculation_result.clear()
        for var_input in self.var_inputs:
            var_input.clear()
    
    # 调试过程功能
    def debug_process(self):
        infix_expr = self.debug_infix_input.text().strip()
        if not infix_expr:
            QMessageBox.warning(self, "输入错误", "请输入中缀表达式")
            return
            
        try:
            # 确保表达式以#结尾
            if not infix_expr.endswith('#'):
                infix_expr += '#'
                
            # 转换过程跟踪
            postfix_expr, process_table = self.debugger.trace_infix_to_postfix(infix_expr)
            
            # 显示中缀到后缀的转换过程
            self.infix_to_postfix_table.setRowCount(len(process_table))
            for i, row in enumerate(process_table):
                self.infix_to_postfix_table.setItem(i, 0, QTableWidgetItem(str(row["步骤"])))
                self.infix_to_postfix_table.setItem(i, 1, QTableWidgetItem(str(row["当前符号"])))
                self.infix_to_postfix_table.setItem(i, 2, QTableWidgetItem(str(row["输入区"])))
                self.infix_to_postfix_table.setItem(i, 3, QTableWidgetItem(str(row["运算符栈"])))
                self.infix_to_postfix_table.setItem(i, 4, QTableWidgetItem(str(row["输出区"])))
            
            # 解析变量赋值
            variables = {}
            var_input_text = self.debug_var_input.text().strip()
            if var_input_text:
                for assignment in var_input_text.rstrip(';').split(';'):
                    if assignment.strip():
                        try:
                            name, value = assignment.split('=')
                            name = name.strip()
                            value = float(value.strip())
                            variables[name] = value
                        except:
                            QMessageBox.warning(self, "输入错误", f"变量赋值格式错误: '{assignment}'，正确格式应为 'name=value'")
                            return
            
            # 计算后缀表达式
            result, eval_process = self.debugger.trace_postfix_evaluation(postfix_expr, variables)
            
            # 显示后缀表达式计算过程
            self.postfix_eval_table.setRowCount(len(eval_process))
            for i, row in enumerate(eval_process):
                self.postfix_eval_table.setItem(i, 0, QTableWidgetItem(str(row["步骤"])))
                self.postfix_eval_table.setItem(i, 1, QTableWidgetItem(str(row["当前符号"])))
                
                stack_str = ', '.join(str(x) for x in row["栈内容"])
                self.postfix_eval_table.setItem(i, 2, QTableWidgetItem(stack_str))
                
                explanation = row.get("说明", "")
                self.postfix_eval_table.setItem(i, 3, QTableWidgetItem(str(explanation)))
            
            # 显示最终结果
            self.debug_result.setText(str(result))
            
        except Exception as e:
            QMessageBox.critical(self, "调试错误", f"调试过程中发生错误: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RPNCalculatorApp()
    window.show()
    sys.exit(app.exec()) 