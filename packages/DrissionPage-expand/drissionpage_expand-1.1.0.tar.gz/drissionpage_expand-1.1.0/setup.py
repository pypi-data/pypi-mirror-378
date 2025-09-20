#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

# 读取README文件
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return """
# DrissionPage扩展包

提供异步请求功能，通过HTTP服务器中转实现，完全兼容requests使用方式。

## 主要功能

- 异步HTTP请求支持
- 完全兼容requests API
- 自动启动HTTP服务器
- 支持批量请求
- 表单数据自动处理

## 安装

```bash
pip install DrissionPage-expand
```

## 使用示例

```python
import DrissionPage_expand as dpe
from DrissionPage import ChromiumPage

page = ChromiumPage()
response = dpe.get(page, 'https://api.example.com')
print(response.status_code)  # 完全兼容requests API
print(response.json())
```
"""

# 读取版本信息
def get_version():
    version_file = os.path.join(os.path.dirname(__file__), '__init__.py')
    with open(version_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"').strip("'")
    return '1.1.0'

setup(
    name='DrissionPage-expand',
    version=get_version(),
    author='DrissionPage Expand',
    author_email='drissionpage.expand@example.com',
    description='DrissionPage扩展包，提供异步请求功能，通过HTTP服务器中转实现',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/DrissionPage/DrissionPage-expand',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Testing',
    ],
    python_requires='>=3.7',
    install_requires=[
        'Flask>=2.0.0',
        'Flask-CORS>=3.0.0',
        'DrissionPage>=4.0.0',
    ],
    keywords='drissionpage async request http automation web scraping',
    project_urls={
        'Bug Reports': 'https://github.com/DrissionPage/DrissionPage-expand/issues',
        'Source': 'https://github.com/DrissionPage/DrissionPage-expand',
        'Documentation': 'https://github.com/DrissionPage/DrissionPage-expand/blob/main/README.md',
    },
    include_package_data=True,
    zip_safe=False,
)
