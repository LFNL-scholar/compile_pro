#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
词法分析器可视化界面
基于PyQt6实现词法分析器的图形用户界面
"""

import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QTextEdit, QPushButton, QTableWidget, 
                           QTableWidgetItem, QFileDialog, QTabWidget, QLabel,
                           QSplitter, QListWidget, QMessageBox)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon, QColor

# 导入词法分析器模块
from lexical_analyzer import LexicalAnalyzer, TYPE_KEYWORD, TYPE_DELIMITER, TYPE_OPERATOR, TYPE_RELATIONAL, TYPE_CONSTANT, TYPE_IDENTIFIER

class LexicalAnalyzerUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.analyzer = LexicalAnalyzer()
        self.init_ui()
        
    def init_ui(self):
        # 设置窗口属性
        self.setWindowTitle('词法分析器')
        self.resize(1200, 800)
        
        # 创建中央控件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Vertical)
        main_layout.addWidget(splitter)
        
        # 创建上方编辑区域
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        splitter.addWidget(top_widget)
        
        # 代码输入区域
        self.code_editor = QTextEdit()
        self.code_editor.setFont(QFont('Courier New', 12))
        self.code_editor.setPlaceholderText('在此处输入代码...')
        top_layout.addWidget(self.code_editor)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.load_file_btn = QPushButton('打开文件')
        self.load_file_btn.clicked.connect(self.load_file)
        button_layout.addWidget(self.load_file_btn)
        
        self.analyze_btn = QPushButton('开始分析')
        self.analyze_btn.clicked.connect(self.analyze_code)
        button_layout.addWidget(self.analyze_btn)
        
        self.clear_btn = QPushButton('清空')
        self.clear_btn.clicked.connect(self.clear_all)
        button_layout.addWidget(self.clear_btn)
        
        top_layout.addLayout(button_layout)
        
        # 创建下方结果显示区域
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        splitter.addWidget(bottom_widget)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        bottom_layout.addWidget(self.tab_widget)
        
        # 词法单元表
        self.token_table = QTableWidget()
        self.token_table.setColumnCount(5)
        self.token_table.setHorizontalHeaderLabels(['单词', '类型', '属性值', '行号', '列号'])
        self.token_table.horizontalHeader().setStretchLastSection(True)
        self.tab_widget.addTab(self.token_table, '词法单元')
        
        # 标识符表
        self.identifier_list = QListWidget()
        self.tab_widget.addTab(self.identifier_list, '标识符表')
        
        # 常数表
        self.constant_list = QListWidget()
        self.tab_widget.addTab(self.constant_list, '常数表')
        
        # 错误信息
        self.error_table = QTableWidget()
        self.error_table.setColumnCount(3)
        self.error_table.setHorizontalHeaderLabels(['错误', '行号', '列号'])
        self.error_table.horizontalHeader().setStretchLastSection(True)
        self.tab_widget.addTab(self.error_table, '错误信息')
        
        # 设置状态栏
        self.status_bar = self.statusBar()
        
        # 设置窗口比例
        splitter.setSizes([400, 400])
    
    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "打开文件", "", "所有文件 (*)")
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.code_editor.setText(f.read())
                self.status_bar.showMessage(f'已加载文件: {file_path}')
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法打开文件: {e}")
    
    def analyze_code(self):
        # 获取代码内容
        code = self.code_editor.toPlainText()
        
        if not code.strip():
            QMessageBox.warning(self, "警告", "请先输入或加载代码")
            return
        
        # 执行词法分析
        self.analyzer.load_string(code)
        tokens = self.analyzer.analyze()
        
        # 清空之前的结果
        self.token_table.setRowCount(0)
        self.identifier_list.clear()
        self.constant_list.clear()
        self.error_table.setRowCount(0)
        
        # 更新词法单元表
        self.token_table.setRowCount(len(tokens))
        error_count = 0
        
        for i, token in enumerate(tokens):
            # 单词
            self.token_table.setItem(i, 0, QTableWidgetItem(token['value']))
            
            if token['type'] == 'Error':
                # 错误处理
                self.token_table.setItem(i, 1, QTableWidgetItem('错误'))
                self.token_table.setItem(i, 2, QTableWidgetItem('N/A'))
                
                # 添加到错误表
                self.error_table.insertRow(error_count)
                self.error_table.setItem(error_count, 0, QTableWidgetItem(token['error_msg']))
                self.error_table.setItem(error_count, 1, QTableWidgetItem(str(token['line'])))
                self.error_table.setItem(error_count, 2, QTableWidgetItem(str(token['column'])))
                error_count += 1
                
                # 设置错误行的颜色
                for col in range(5):
                    if self.token_table.item(i, col):
                        self.token_table.item(i, col).setBackground(QColor(255, 200, 200))
            else:
                # 正常token处理
                type_name = self.analyzer.get_type_name(token['type'])
                attribute = self.analyzer.get_token_attribute(token)
                
                self.token_table.setItem(i, 1, QTableWidgetItem(type_name))
                self.token_table.setItem(i, 2, QTableWidgetItem(str(attribute)))
            
            # 位置信息
            self.token_table.setItem(i, 3, QTableWidgetItem(str(token['line'])))
            self.token_table.setItem(i, 4, QTableWidgetItem(str(token['column'])))
        
        # 更新标识符表
        from lexical_analyzer import identifiers
        for identifier in identifiers:
            self.identifier_list.addItem(identifier)
        
        # 更新常数表
        from lexical_analyzer import constants
        for constant in constants:
            self.constant_list.addItem(constant)
        
        # 更新状态栏
        self.status_bar.showMessage(f'分析完成: {len(tokens)}个词法单元, {len(identifiers)}个标识符, {len(constants)}个常数, {error_count}个错误')
        
        # 自动切换到错误标签页(如果有错误)
        if error_count > 0:
            self.tab_widget.setCurrentIndex(3)
    
    def clear_all(self):
        # 清空代码编辑器
        self.code_editor.clear()
        
        # 清空结果
        self.token_table.setRowCount(0)
        self.identifier_list.clear()
        self.constant_list.clear()
        self.error_table.setRowCount(0)
        
        # 重置词法分析器状态
        from lexical_analyzer import identifiers, constants
        identifiers.clear()
        constants.clear()
        self.analyzer = LexicalAnalyzer()
        
        # 更新状态栏
        self.status_bar.showMessage('已清空')

def main():
    app = QApplication(sys.argv)
    window = LexicalAnalyzerUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 