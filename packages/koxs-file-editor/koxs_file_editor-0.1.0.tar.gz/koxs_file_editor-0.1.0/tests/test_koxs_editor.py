#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
koxs文件编辑器测试用例
"""

import unittest
import os
import tempfile
from koxs_file_editor import koxsFileEditor

class TestKoxsEditor(unittest.TestCase):
    
    def setUp(self):
        """测试前准备"""
        self.test_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
        self.test_file.write("Line 1\nLine 2\nLine 3\n")
        self.test_file.close()
        
    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.test_file.name):
            os.unlink(self.test_file.name)
    
    def test_basic_operations(self):
        """测试基本操作"""
        editor = koxsFileEditor(self.test_file.name)
        
        # 测试获取行
        line = editor.koxs_get_line(0)
        self.assertEqual(line, "Line 1\n")
        
        # 测试追加行
        editor.koxs_append_line("Line 4")
        self.assertEqual(editor.koxs_get_line_count(), 4)
        
        # 测试设置行
        editor.koxs_set_line(0, "Modified Line 1")
        self.assertEqual(editor.koxs_get_line(0), "Modified Line 1")
    
    def test_undo_redo(self):
        """测试撤销重做"""
        editor = koxsFileEditor(self.test_file.name)
        
        original_content = editor.koxs_get_all_lines().copy()
        
        # 修改内容
        editor.koxs_append_line("New Line")
        
        # 撤销
        editor.koxs_undo()
        self.assertEqual(editor.koxs_get_all_lines(), original_content)
        
        # 重做
        editor.koxs_redo()
        self.assertEqual(editor.koxs_get_line_count(), 4)
    
    def test_regex_operations(self):
        """测试正则表达式操作"""
        editor = koxsFileEditor(self.test_file.name)
        
        # 测试正则替换
        editor.koxs_replace_regex(r'Line', 'Row')
        content = editor.koxs_get_all_lines()
        self.assertTrue(all('Row' in line for line in content))
        
        # 测试正则查找
        matches = editor.koxs_find_regex(r'Row')
        self.assertEqual(len(matches), 3)
    
    def test_batch_operations(self):
        """测试批量操作"""
        editor = koxsFileEditor(self.test_file.name)
        
        operations = [
            {'type': 'append_line', 'content': 'Batch Line 1'},
            {'type': 'append_line', 'content': 'Batch Line 2'},
            {'type': 'delete_line', 'line': 0}
        ]
        
        results = editor.koxs_batch_operations(operations)
        self.assertEqual(len(results), 3)
        self.assertEqual(editor.koxs_get_line_count(), 4)

if __name__ == '__main__':
    unittest.main()