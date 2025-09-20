# DrissionPage扩展包

[![PyPI version](https://badge.fury.io/py/DrissionPage-expand.svg)](https://badge.fury.io/py/DrissionPage-expand)
[![Python versions](https://img.shields.io/pypi/pyversions/DrissionPage-expand.svg)](https://pypi.org/project/DrissionPage-expand/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

DrissionPage扩展包，提供异步请求功能，通过HTTP服务器中转实现，完全兼容requests使用方式。

## 主要功能

- ✅ **异步HTTP请求支持** - 在DrissionPage中实现真正的异步请求
- ✅ **完全兼容requests API** - 无缝替换requests使用方式
- ✅ **自动启动HTTP服务器** - 导入时自动启动，无需手动配置
- ✅ **支持批量请求** - 高效处理多个并发请求
- ✅ **表单数据自动处理** - 自动处理form_data参数
- ✅ **请求信息记录** - 完整记录请求参数和响应信息
- ✅ **错误重试机制** - 自动重试失败的请求

## 安装

```bash
pip install DrissionPage-expand
```

## 快速开始

### 基本使用

```python
import DrissionPage_expand as dpe
from DrissionPage import ChromiumPage

# 创建页面实例
page = ChromiumPage()

# 发送GET请求 - 完全兼容requests API
response = dpe.get(page, 'https://httpbin.org/get')
print(response.status_code)  # 200
print(response.json())       # 响应JSON数据
print(response.text)         # 响应文本
response.raise_for_status()  # 检查状态码

# 发送POST请求
response = dpe.post(page, 'https://httpbin.org/post', 
                   json={'key': 'value'})
```

### 表单数据提交

```python
# 使用form_data参数自动处理表单数据
form_data = {
    'username': 'test_user',
    'password': 'test_password',
    'email': 'test@example.com'
}

response = dpe.post(page, 'https://httpbin.org/post', 
                   form_data=form_data)
```

### 批量请求

```python
# 批量发送多个请求
requests = [
    {'method': 'GET', 'url': 'https://httpbin.org/get'},
    {'method': 'POST', 'url': 'https://httpbin.org/post', 'json': {'data': 'test'}},
    {'method': 'PUT', 'url': 'https://httpbin.org/put', 'json': {'update': 'data'}}
]

responses = dpe.batch_request(page, requests)
for response in responses:
    if response:
        print(f"状态码: {response.status_code}")
```

## API文档

### 主要方法

- `get(tab, url, **kwargs)` - 发送GET请求
- `post(tab, url, **kwargs)` - 发送POST请求  
- `put(tab, url, **kwargs)` - 发送PUT请求
- `delete(tab, url, **kwargs)` - 发送DELETE请求
- `patch(tab, url, **kwargs)` - 发送PATCH请求
- `async_request(tab, method, url, **kwargs)` - 通用异步请求方法
- `batch_request(tab, requests, **kwargs)` - 批量请求

### Response对象

Response对象完全兼容requests.Response，支持以下属性和方法：

```python
# requests风格的属性
response.status_code    # HTTP状态码
response.reason         # 状态文本
response.url           # 请求URL
response.ok            # 是否成功
response.headers       # 响应头
response.content       # 响应内容(bytes)
response.text          # 响应文本(str)
response.json()        # 解析JSON响应
response.raise_for_status()  # 检查状态码

# 向后兼容的属性
response.status        # 等同于status_code
response.status_text   # 等同于reason
response.data          # 原始响应数据
response.is_success()  # 等同于ok
response.get_header(name)  # 获取指定响应头
```

## 参数说明

### 请求参数

- `headers` - 请求头字典
- `data` - 请求体数据（JSON格式）
- `form_data` - 表单数据（字典格式，自动转换为application/x-www-form-urlencoded）
- `params` - URL参数
- `timeout` - 请求超时时间（秒）
- `server_timeout` - 等待服务器响应的超时时间（秒）
- `retry_timeout` - 是否对失败请求进行重试
- `max_retries` - 最大重试次数

### 重试条件

- 请求超时 (TimeoutError)
- 服务器错误状态码 (5xx)
- 网络错误 (状态码为0)

## 高级用法

### 自定义服务器配置

```python
# 使用自定义服务器
server = dpe.RequestResponseServer(host='127.0.0.1', port=9999)
server.start()

# 使用完毕后停止服务器
server.stop()
```

### 错误处理

```python
try:
    response = dpe.get(page, 'https://httpbin.org/status/404')
    response.raise_for_status()  # 抛出HTTPError异常
except Exception as e:
    print(f"请求失败: {e}")
```

## 与requests对比

| 功能 | requests | DrissionPage-expand |
|------|----------|-------------------|
| 基本请求 | `requests.get(url)` | `dpe.get(tab, url)` |
| 状态码 | `response.status_code` | `response.status_code` |
| 响应文本 | `response.text` | `response.text` |
| JSON解析 | `response.json()` | `response.json()` |
| 状态检查 | `response.raise_for_status()` | `response.raise_for_status()` |
| 异步支持 | ❌ | ✅ |
| 浏览器环境 | ❌ | ✅ |

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 更新日志

### v1.1.0
- 完全兼容requests API
- 自动启动HTTP服务器
- 支持表单数据处理
- 添加批量请求功能
- 改进错误处理和重试机制
