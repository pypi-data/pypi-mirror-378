# Form Data 使用说明

## 概述

现在项目支持通过 `form_data` 参数自动发送表单数据，无需手动进行URL编码。

## 新增功能

### 1. `form_data` 参数

- **类型**: 字典 (dict)
- **用途**: 自动转换为 `application/x-www-form-urlencoded` 格式
- **自动设置**: `Content-Type: application/x-www-form-urlencoded`

### 2. 支持的方法

- `async_request()` - 主要异步请求方法
- `get()`, `post()`, `put()`, `delete()`, `patch()` - 便捷方法
- `batch_request()` - 批量请求

## 使用示例

### 基本用法

```python
import xhr_request as dpe
from DrissionPage import ChromiumPage

page = ChromiumPage()

# 发送表单数据
form_data = {
    'username': 'test_user',
    'password': 'test_password',
    'email': 'test@example.com'
}

response = dpe.post(page, 'https://example.com/login', 
                   form_data=form_data)
```

### GET请求中的form_data

```python
# GET请求中，form_data会自动转换为URL参数
response = dpe.get(page, 'https://example.com/search',
                  form_data={'q': '搜索关键词', 'page': '1'})
# 实际请求URL: https://example.com/search?q=搜索关键词&page=1
```

### 批量请求

```python
batch_requests = [
    {
        'method': 'POST',
        'url': 'https://example.com/api/user1',
        'form_data': {'name': 'user1', 'action': 'update'}
    },
    {
        'method': 'POST',
        'url': 'https://example.com/api/user2', 
        'form_data': {'name': 'user2', 'action': 'create'}
    }
]

responses = dpe.batch_request(page, batch_requests)
```

### 复杂表单数据

```python
# 支持复杂的表单字段名
complex_form = {
    'user[name]': '张三',
    'user[email]': 'zhangsan@example.com',
    'user[preferences][]': 'music',
    'user[settings][theme]': 'dark',
    'submit': '提交'
}

response = dpe.post(page, 'https://example.com/profile',
                   form_data=complex_form)
```

## 与传统方式的对比

### 使用 form_data (新方式)
```python
# 简单直接
response = dpe.post(page, url, form_data={'key': 'value'})
```

### 使用 data (传统方式)
```python
from urllib.parse import urlencode

# 需要手动编码
data = urlencode({'key': 'value'})
response = dpe.post(page, url, 
                   data=data,
                   headers={'Content-Type': 'application/x-www-form-urlencoded'})
```

## 注意事项

1. **互斥参数**: `data` 和 `form_data` 不能同时使用
2. **自动编码**: `form_data` 会自动进行URL编码
3. **自动设置Content-Type**: 无需手动设置请求头
4. **GET请求优化**: GET请求中的 `form_data` 自动转换为URL参数
5. **类型检查**: `form_data` 必须是字典类型

## 错误处理

```python
try:
    # 错误：同时使用data和form_data
    response = dpe.post(page, url, 
                       data={'key1': 'value1'},
                       form_data={'key2': 'value2'})
except ValueError as e:
    print(f"错误: {e}")
    # 输出: 错误: data和form_data参数不能同时使用，请选择其中一个

try:
    # 错误：form_data不是字典类型
    response = dpe.post(page, url, form_data="invalid")
except ValueError as e:
    print(f"错误: {e}")
    # 输出: 错误: form_data参数必须是字典类型
```

## 完整示例

参见 `form_data_example.py` 文件，包含了各种使用场景的完整示例。

## 兼容性

- 完全向后兼容，现有代码无需修改
- 新的 `form_data` 参数是可选的
- 所有现有功能保持不变
