"""
HTTP服务器，用于接收和存储异步请求的响应数据
支持跨域请求
使用Flask实现，稳定可靠，添加了自动端口分配功能
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import time
import uuid
import socket
from typing import Dict, Any, Optional
import logging

# 配置日志 - 设置为WARNING级别以减少输出
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


def find_free_port(start_port=8888, max_attempts=100):
    """
    查找可用的端口

    Args:
        start_port: 起始端口号
        max_attempts: 最大尝试次数

    Returns:
        可用的端口号，如果找不到则返回None
    """
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    return None


# Flask实现，稳定可靠


class RequestResponseServer:
    def __init__(self, host='localhost', port=None):
        self.app = Flask(__name__)
        CORS(self.app)  # 允许跨域

        self.host = host
        # 如果没有指定端口，自动查找可用端口
        if port is None:
            self.port = find_free_port()
            if self.port is None:
                raise RuntimeError("无法找到可用的端口")
        else:
            # 检查指定端口是否可用
            if not self._is_port_available(port):
                # 如果指定端口不可用，从该端口开始查找
                available_port = find_free_port(port)
                if available_port is None:
                    raise RuntimeError(f"端口 {port} 不可用，且无法找到其他可用端口")
                self.port = available_port
                logger.warning(f"端口 {port} 不可用，使用端口 {self.port}")
            else:
                self.port = port

        self.response_storage: Dict[str, Any] = {}  # 存储请求ID和响应数据
        self.server_thread = None
        self.is_running = False

        self._setup_routes()

    def _is_port_available(self, port):
        """检查端口是否可用"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((self.host, port))
                return True
        except OSError:
            return False

    def _setup_routes(self):
        """设置路由"""

        @self.app.route('/store_response', methods=['POST', 'OPTIONS'])
        def store_response():
            """接收JS发送的响应数据"""
            if request.method == 'OPTIONS':
                # 处理预检请求
                response = jsonify({'status': 'ok'})
                response.headers.add('Access-Control-Allow-Origin', '*')
                response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
                response.headers.add('Access-Control-Allow-Methods', 'POST')
                return response

            try:
                data = request.get_json()
                request_id = data.get('request_id')
                response_data = data.get('response_data')

                if not request_id:
                    return jsonify({'error': 'Missing request_id'}), 400

                # 存储响应数据
                self.response_storage[request_id] = response_data

                return jsonify({'status': 'success'})

            except Exception as e:
                logger.error(f"Error storing response: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/get_response/<request_id>', methods=['GET'])
        def get_response(request_id):
            """获取指定请求ID的响应数据"""
            response_data = self.response_storage.get(request_id)
            if response_data is not None:
                # 获取后删除数据
                del self.response_storage[request_id]
                return jsonify({'status': 'success', 'data': response_data})
            else:
                return jsonify({'status': 'pending'}), 202

        @self.app.route('/health', methods=['GET'])
        def health():
            """健康检查"""
            return jsonify({'status': 'healthy', 'storage_count': len(self.response_storage)})

    def start(self):
        """启动服务器"""
        if self.is_running:
            return

        def run_server():
            # 禁用Flask相关的日志输出
            import logging
            import os

            # 设置环境变量禁用Flask CLI输出
            os.environ['FLASK_ENV'] = 'production'

            # 禁用所有相关的logger
            logging.getLogger('werkzeug').setLevel(logging.ERROR)
            logging.getLogger('werkzeug').disabled = True

            self.app.run(host=self.host, port=self.port, debug=False, use_reloader=False)

        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        self.is_running = True

        # 等待服务器启动
        time.sleep(1)

    def stop(self):
        """停止服务器"""
        self.is_running = False

    def wait_for_response(self, request_id: str, timeout: int = 30) -> Optional[Any]:
        """等待指定请求ID的响应数据"""
        start_time = time.time()

        while time.time() - start_time < timeout:
            if request_id in self.response_storage:
                response_data = self.response_storage.pop(request_id)
                return response_data
            time.sleep(0.1)  # 100ms检查一次

        return None  # 超时

    def generate_request_id(self) -> str:
        """生成唯一的请求ID"""
        return str(uuid.uuid4())


# 全局服务器实例
_server_instance = None


def get_server(host='localhost', port=None) -> RequestResponseServer:
    """
    获取服务器实例（单例模式）

    Args:
        host: 服务器主机地址
        port: 服务器端口，如果为None则自动查找可用端口

    Returns:
        RequestResponseServer实例
    """
    global _server_instance
    if _server_instance is None:
        _server_instance = RequestResponseServer(host, port)
        _server_instance.start()
        logger.info(f"Flask HTTP服务器已启动: http://{_server_instance.host}:{_server_instance.port}")
    return _server_instance


def stop_server():
    """停止服务器"""
    global _server_instance
    if _server_instance:
        _server_instance.stop()
        _server_instance = None


if __name__ == '__main__':
    # 测试服务器
    server = RequestResponseServer()
    server.start()

    try:
        print("Server is running. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop()
        print("Server stopped.")
