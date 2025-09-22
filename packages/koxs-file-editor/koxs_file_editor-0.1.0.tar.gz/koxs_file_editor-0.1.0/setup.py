#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

# 读取README内容
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

# 读取版本号
with open(os.path.join('koxs_file_editor', '__init__.py'), 'r', encoding='utf-8') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.split('=')[1].strip().strip('"\'')
            break

setup(
    name="koxs-file-editor",
    version=version,
    author="koxs",
    author_email="koxs@example.com",
    description="一个功能强大的纯Python文件编辑器，支持批量操作、撤销重做、大文件处理和正则表达式",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/koxs-file-editor",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Topic :: Text Editors",
        "Topic :: Text Processing",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    keywords="file editor, text processing, batch operations, undo redo, regex, large files",
    project_urls={
        "Documentation": "https://github.com/yourusername/koxs-file-editor/wiki",
        "Source": "https://github.com/yourusername/koxs-file-editor",
        "Tracker": "https://github.com/yourusername/koxs-file-editor/issues",
    },
    include_package_data=True,
)