"""
DrissionPage扩展包
提供异步请求功能，通过HTTP服务器中转实现
"""

from .xhr_request import async_request, get, post, put, delete, patch, batch_request, Response
from .http_server import get_server, stop_server, RequestResponseServer

__version__ = "1.1.0"
__author__ = "DrissionPage Expand"

__all__ = [
    'async_request', 'batch_request', 'Response',
    'get', 'post', 'put', 'delete', 'patch',
    'get_server', 'stop_server', 'RequestResponseServer'
]

# 在导入时自动启动HTTP服务器
try:
    _server = get_server()
except Exception:
    # 如果启动失败，不影响导入
    pass
