"""
异步请求模块
通过DrissionPage的tab对象和HTTP服务器实现异步请求处理
"""

import json
import time
from typing import Dict, Any, Optional, Union, List, Iterator
from urllib.parse import urlencode
try:
    from .http_server import get_server, RequestResponseServer
except ImportError:
    from http_server import get_server, RequestResponseServer
    from http_server import get_server, RequestResponseServer


class Response:
    """
    HTTP响应类，封装请求响应数据
    兼容requests.Response的接口
    """

    def __init__(self, response_data: Optional[Dict[str, Any]] = None, request_info: Optional[Dict[str, Any]] = None):
        """
        初始化响应对象

        Args:
            response_data: 从服务器获取的响应数据字典
            request_info: 原始请求信息字典，包含method, url, headers, data, params等
        """
        if response_data is None:
            response_data = {}

        self._raw_data = response_data

        # 基本属性（保持向后兼容）
        self.status = response_data.get('status', 0)
        self.status_text = response_data.get('statusText', '')
        self.headers = response_data.get('headers', {})
        self.data = response_data.get('data')
        self.url = response_data.get('url', '')
        self.ok = response_data.get('ok', False)

        # requests兼容属性
        self.status_code = self.status  # requests使用status_code
        self.reason = self.status_text  # requests使用reason

        # 错误信息
        self.error = response_data.get('error', False)
        self.error_message = response_data.get('message', '')
        self.error_name = response_data.get('name', '')
        self.error_stack = response_data.get('stack', '')

        # 请求信息
        self.request = request_info or {}

        # requests兼容的额外属性
        self.cookies = {}  # 空的cookies字典
        self.elapsed = None  # 请求耗时，暂时设为None
        self.encoding = 'utf-8'  # 默认编码
        self.history = []  # 重定向历史，空列表
        self.raw = None  # 原始响应对象，设为None

    def json(self) -> Any:
        """
        获取JSON格式的响应数据

        Returns:
            解析后的JSON数据，如果不是JSON格式则返回原始数据
        """
        if isinstance(self.data, (dict, list)):
            return self.data

        if isinstance(self.data, str):
            try:
                return json.loads(self.data)
            except (json.JSONDecodeError, TypeError):
                return self.data

        return self.data

    @property
    def content(self) -> bytes:
        """
        获取响应内容的字节形式（requests兼容属性）

        Returns:
            响应内容的字节形式
        """
        if isinstance(self.data, str):
            return self.data.encode('utf-8')
        elif isinstance(self.data, bytes):
            return self.data
        elif self.data is not None:
            return str(self.data).encode('utf-8')
        else:
            return b''

    @property
    def text(self) -> str:
        """
        获取文本格式的响应数据（requests兼容属性）

        Returns:
            字符串格式的响应数据
        """
        if isinstance(self.data, str):
            return self.data
        elif self.data is not None:
            return str(self.data)
        else:
            return ''

    def is_success(self) -> bool:
        """
        判断请求是否成功

        Returns:
            True表示成功（状态码2xx且无错误），False表示失败
        """
        return self.ok and not self.error and 200 <= self.status < 300

    def is_client_error(self) -> bool:
        """
        判断是否为客户端错误（4xx）

        Returns:
            True表示客户端错误，False表示不是
        """
        return 400 <= self.status < 500

    def is_server_error(self) -> bool:
        """
        判断是否为服务器错误（5xx）

        Returns:
            True表示服务器错误，False表示不是
        """
        return 500 <= self.status < 600

    def get_header(self, name: str, default: str = '') -> str:
        """
        获取指定的响应头

        Args:
            name: 响应头名称（不区分大小写）
            default: 默认值

        Returns:
            响应头值
        """
        # 不区分大小写查找
        for key, value in self.headers.items():
            if key.lower() == name.lower():
                return value
        return default

    def raise_for_status(self):
        """
        如果响应状态码表示错误，则抛出HTTPError异常（requests兼容方法）
        """
        if 400 <= self.status_code < 600:
            error_msg = f"{self.status_code} {self.reason}"
            if self.url:
                error_msg += f" for url: {self.url}"

            # 创建一个简单的HTTPError异常
            class HTTPError(Exception):
                def __init__(self, message, response=None):
                    super().__init__(message)
                    self.response = response

            raise HTTPError(error_msg, self)

    def __bool__(self) -> bool:
        """
        布尔值判断，用于 if response: 这样的判断

        Returns:
            True表示有响应数据，False表示无响应或超时
        """
        return self._raw_data is not None and len(self._raw_data) > 0

    def __str__(self) -> str:
        """
        字符串表示（requests兼容格式）
        """
        if self.error:
            return f"<Response [ERROR] {self.error_name}: {self.error_message}>"
        else:
            return f"<Response [{self.status_code}]>"

    def __repr__(self) -> str:
        """
        详细字符串表示
        """
        return self.__str__()

    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式（向后兼容）

        Returns:
            包含所有响应数据的字典
        """
        result = self._raw_data.copy() if self._raw_data else {}
        if self.request:
            result['request'] = self.request
        return result


def async_request(tab, method: str, url: str, **kwargs) -> Optional[Response]:
    """
    通过DrissionPage的tab对象发送异步请求，支持超时和错误状态码重试

    Args:
        tab: DrissionPage的tab对象
        method: 请求方法 (GET, POST, PUT, DELETE等)
        url: 请求URL
        **kwargs: 其他请求参数
            - headers: 请求头字典
            - data: 请求体数据（JSON格式）
            - form_data: 表单数据（字典格式，自动转换为application/x-www-form-urlencoded）
            - params: URL参数
            - timeout: 超时时间（秒）
            - force_timeout: 强制超时时间（秒），优先级高于timeout
            - server_timeout: 等待服务器响应的超时时间（秒）
            - retry_timeout: 是否对失败请求进行重试（默认True）
            - max_retries: 最大重试次数（默认1）

    Returns:
        Response对象，包含status, headers, data等信息
        如果超时或出错返回None

    重试条件:
        - 请求超时 (TimeoutError)
        - 服务器错误状态码 (5xx)
        - 网络错误 (状态码为0)

    注意:
        - data和form_data参数不能同时使用
        - form_data会自动设置Content-Type为application/x-www-form-urlencoded
    """

    # 提取参数
    headers = kwargs.get('headers', {})
    data = kwargs.get('data')
    form_data = kwargs.get('form_data')
    params = kwargs.get('params', {})
    timeout = kwargs.get('timeout', 30)
    server_timeout = kwargs.get('server_timeout', 35)
    retry_timeout = kwargs.get('retry_timeout', True)
    max_retries = kwargs.get('max_retries', 1)
    force_timeout = kwargs.get('force_timeout', None)  # 强制超时时间（秒）

    # 检查data和form_data不能同时使用
    if data is not None and form_data is not None:
        raise ValueError("data和form_data参数不能同时使用，请选择其中一个")

    # 处理form_data参数
    if form_data is not None:
        if not isinstance(form_data, dict):
            raise ValueError("form_data参数必须是字典类型")
        # 将form_data转换为URL编码格式
        data = urlencode(form_data)
        # 自动设置Content-Type
        if 'Content-Type' not in headers:
            headers['Content-Type'] = 'application/x-www-form-urlencoded'

    # 获取服务器实例
    server = get_server()

    # 构造请求信息
    request_info = {
        'method': method,
        'url': url,
        'headers': headers,
        'data': data,
        'params': params,
        'timeout': timeout,
        'force_timeout': force_timeout
    }

    # 尝试发送请求，包括重试逻辑
    for attempt in range(max_retries + 1):  # 原始请求 + 重试次数
        # 生成唯一请求ID
        request_id = server.generate_request_id()

        # 构造JS代码
        js_code = _build_js_request_code(
            request_id=request_id,
            method=method,
            url=url,
            headers=headers,
            data=data,
            params=params,
            timeout=timeout,
            force_timeout=force_timeout,
            server_url=f"http://{server.host}:{server.port}"
        )

        try:
            # 执行JS代码
            tab.run_js(js_code)

            # 等待服务器接收响应数据
            response_data = server.wait_for_response(request_id, server_timeout)

            # 返回Response对象
            if response_data is not None:
                response = Response(response_data, request_info)

                # 检查是否需要重试（超时错误或服务器错误状态码）
                should_retry = (retry_timeout and attempt < max_retries and (
                    # 超时错误
                    (response.error and response.error_name == 'TimeoutError') or
                    # 服务器错误状态码 (5xx) 或网络错误 (0)
                    (response.status >= 500 or response.status == 0)
                ))

                if should_retry:
                    if response.error and response.error_name == 'TimeoutError':
                        print(f"请求超时，进行第 {attempt + 1} 次重试: {url}")
                    elif response.status >= 500:
                        print(f"服务器错误 ({response.status})，进行第 {attempt + 1} 次重试: {url}")
                    elif response.status == 0:
                        print(f"网络错误，进行第 {attempt + 1} 次重试: {url}")
                    continue  # 继续下一次尝试

                return response
            else:
                # 无响应数据，如果启用重试且还有重试次数，则继续重试
                if retry_timeout and attempt < max_retries:
                    print(f"请求无响应，进行第 {attempt + 1} 次重试: {url}")
                    continue
                return None

        except Exception as e:
            # 如果是最后一次尝试或不需要重试，返回错误响应
            if attempt == max_retries or not retry_timeout:
                # print(f"Error in async_request: {e}")  # 移除日志输出
                error_data = {
                    'error': True,
                    'message': str(e),
                    'name': type(e).__name__,
                    'status': 0,
                    'ok': False
                }
                return Response(error_data, request_info)
            else:
                print(f"请求异常，进行第 {attempt + 1} 次重试: {url}, 错误: {e}")
                continue

    # 如果所有重试都失败了，返回None
    return None


def _build_js_request_code(request_id: str, method: str, url: str,
                           headers: Dict[str, str], data: Any,
                           params: Dict[str, str], timeout: int,
                           force_timeout: Optional[int],
                           server_url: str) -> str:
    """
    构造执行异步请求的JS代码
    """

    # 处理URL参数和GET方法的data优化
    url_params = {}
    if params:
        url_params.update(params)

    # GET方法优化：将data字典转换为URL参数
    if method.upper() == 'GET' and data is not None:
        if isinstance(data, dict):
            url_params.update(data)
            data = None  # GET请求不应该有请求体
        elif isinstance(data, str) and '=' in data:
            # 如果data是URL编码的字符串（来自form_data），直接添加到URL
            url = f"{url}?{data}" if '?' not in url else f"{url}&{data}"
            data = None  # GET请求不应该有请求体

    # 构建最终URL（使用正确的URL编码）
    if url_params:
        param_str = urlencode(url_params)
        url = f"{url}?{param_str}" if '?' not in url else f"{url}&{param_str}"

    # 处理请求体数据
    data_js = "null"
    if data is not None:
        if isinstance(data, dict):
            # 将字典转换为JSON字符串，并在JavaScript中作为字符串字面量
            json_str = json.dumps(data)
            data_js = json.dumps(json_str)  # 双重编码，确保在JS中是字符串
            if 'Content-Type' not in headers:
                headers['Content-Type'] = 'application/json'
        else:
            data_js = json.dumps(str(data))

    # 处理请求头
    headers_js = json.dumps(headers)

    js_code = f"""
(function() {{
    const requestId = '{request_id}';
    const serverUrl = '{server_url}';

    // 发送结果到服务器的函数
    function sendResult(result) {{
        const xhr = new XMLHttpRequest();
        xhr.open('POST', serverUrl + '/store_response', true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.send(JSON.stringify({{ request_id: requestId, response_data: result }}));
    }}

    // 创建XMLHttpRequest对象
    const xhr = new XMLHttpRequest();
    xhr.open('{method.upper()}', '{url}', true);

    // 设置请求头
    const headers = {headers_js};
    Object.keys(headers).forEach(key => xhr.setRequestHeader(key, headers[key]));

    // 设置超时（优先使用强制超时时间）
    xhr.timeout = {(force_timeout or timeout) * 1000};

    // 处理响应
    xhr.onload = function() {{
        let data;
        try {{
            data = JSON.parse(xhr.responseText);
        }} catch (e) {{
            data = xhr.responseText;
        }}

        const result = {{
            status: xhr.status,
            statusText: xhr.statusText,
            headers: {{}}, // XMLHttpRequest无法轻易获取所有响应头
            data: data,
            url: '{url}',
            ok: xhr.status >= 200 && xhr.status < 300
        }};

        sendResult(result);
    }};

    // 处理错误
    xhr.onerror = function() {{
        const errorResult = {{
            error: true,
            message: 'Network error',
            name: 'NetworkError',
            status: 0,
            ok: false
        }};
        sendResult(errorResult);
    }};

    // 处理超时
    xhr.ontimeout = function() {{
        const errorResult = {{
            error: true,
            message: 'Request timeout',
            name: 'TimeoutError',
            status: 0,
            ok: false
        }};
        sendResult(errorResult);
    }};

    // 发送请求
    xhr.send({data_js});
}})();
"""

    return js_code


def _build_batch_js_request_code(request_configs: List[Dict[str, Any]], server_url: str) -> str:
    """构造批量异步请求的JS代码"""

    # 构造请求配置数组
    js_requests = []
    for config in request_configs:
        # 处理URL参数和GET方法的data优化
        url = config['url']
        url_params = {}
        if config['params']:
            url_params.update(config['params'])

        # GET方法优化：将data字典转换为URL参数
        data = config['data']
        if config['method'].upper() == 'GET' and data is not None:
            if isinstance(data, dict):
                url_params.update(data)
                data = None  # GET请求不应该有请求体
            elif isinstance(data, str) and '=' in data:
                # 如果data是URL编码的字符串（来自form_data），直接添加到URL
                url = f"{url}?{data}" if '?' not in url else f"{url}&{data}"
                data = None  # GET请求不应该有请求体

        # 构建最终URL（使用正确的URL编码）
        if url_params:
            param_str = urlencode(url_params)
            url = f"{url}?{param_str}" if '?' not in url else f"{url}&{param_str}"

        # 处理请求体数据
        data_js = "null"
        headers = config['headers'].copy()
        if data is not None:
            if isinstance(data, dict):
                # 将字典转换为JSON字符串，并在JavaScript中作为字符串字面量
                json_str = json.dumps(data)
                data_js = json.dumps(json_str)  # 双重编码，确保在JS中是字符串
                headers.setdefault('Content-Type', 'application/json')
            else:
                data_js = json.dumps(str(data))

        js_request = f"""{{
            requestId: '{config['request_id']}',
            method: '{config['method'].upper()}',
            url: '{url}',
            headers: {json.dumps(headers)},
            data: {data_js},
            timeout: {config['timeout']}
        }}"""
        js_requests.append(js_request)

    js_requests_array = '[' + ','.join(js_requests) + ']'

    js_code = f"""
(function() {{
    const serverUrl = '{server_url}';
    const requests = {js_requests_array};

    console.log(`Starting ${{requests.length}} concurrent requests`);

    // 发送结果到服务器
    function sendResult(requestId, result) {{
        const xhr = new XMLHttpRequest();
        xhr.open('POST', serverUrl + '/store_response', true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.send(JSON.stringify({{ request_id: requestId, response_data: result }}));
    }}

    // 并发发送所有请求
    requests.forEach((config, index) => {{
        const xhr = new XMLHttpRequest();
        xhr.open(config.method, config.url, true);

        // 设置请求头和超时
        Object.keys(config.headers).forEach(key => xhr.setRequestHeader(key, config.headers[key]));
        xhr.timeout = config.timeout;

        xhr.onload = () => {{
            let data;
            try {{ data = JSON.parse(xhr.responseText); }} catch {{ data = xhr.responseText; }}

            sendResult(config.requestId, {{
                status: xhr.status,
                statusText: xhr.statusText,
                headers: {{}},
                data: data,
                url: config.url,
                ok: xhr.status >= 200 && xhr.status < 300
            }});
        }};

        xhr.onerror = () => sendResult(config.requestId, {{
            error: true, message: 'Network error', name: 'NetworkError', status: 0, ok: false
        }});

        xhr.ontimeout = () => sendResult(config.requestId, {{
            error: true, message: 'Request timeout', name: 'TimeoutError', status: 0, ok: false
        }});

        xhr.send(config.data || null);
    }});
}})();


"""

    return js_code


def _wait_for_all_responses(server: RequestResponseServer,
                            request_configs: List[Dict[str, Any]],
                            timeout: int) -> List[Optional[Response]]:
    """等待所有请求的响应"""
    start_time = time.time()
    total_requests = len(request_configs)
    responses = [None] * total_requests

    # 请求ID到索引的映射
    id_to_index = {config['request_id']: config['index'] for config in request_configs}
    pending_ids = set(config['request_id'] for config in request_configs)

    while time.time() - start_time < timeout and pending_ids:
        # 检查新的响应
        completed_ids = []
        for request_id in list(pending_ids):
            if request_id in server.response_storage:
                response_data = server.response_storage.pop(request_id)
                index = id_to_index[request_id]
                # 查找对应的请求配置以获取请求信息
                request_config = None
                for config in request_configs:
                    if config['request_id'] == request_id:
                        request_config = config
                        break

                # 构造请求信息
                request_info = None
                if request_config:
                    request_info = {
                        'method': request_config.get('method', ''),
                        'url': request_config.get('url', ''),
                        'headers': request_config.get('headers', {}),
                        'data': request_config.get('data'),
                        'params': request_config.get('params', {}),
                        'timeout': request_config.get('timeout', 0) / 1000  # 转换回秒
                    }

                responses[index] = Response(response_data, request_info)
                completed_ids.append(request_id)

        # 移除已完成的ID
        pending_ids -= set(completed_ids)

        if pending_ids:
            time.sleep(0.05)  # 50ms检查间隔

    completed = total_requests - len(pending_ids)
    elapsed = time.time() - start_time
    # print(f"Batch request: {completed}/{total_requests} completed in {elapsed:.2f}s")  # 移除日志输出

    return responses


def _retry_timeout_requests(tab, responses: List[Optional[Response]],
                            original_configs: List[Dict[str, Any]],
                            server: RequestResponseServer,
                            server_timeout: int,
                            max_retries: int) -> List[Optional[Response]]:
    """
    对超时的请求进行重试

    Args:
        tab: DrissionPage的tab对象
        responses: 原始响应列表
        original_configs: 原始请求配置列表
        server: 服务器实例
        server_timeout: 服务器超时时间
        max_retries: 最大重试次数

    Returns:
        更新后的响应列表
    """
    retry_count = 0

    while retry_count < max_retries:
        # 找出需要重试的请求（超时或无响应）
        retry_configs = []
        retry_indices = []

        for i, response in enumerate(responses):
            # 检查是否需要重试：无响应、超时错误、服务器错误状态码或网络错误
            should_retry = (
                response is None or
                (response.error and response.error_name == 'TimeoutError') or
                (response.status >= 500 or response.status == 0)
            )

            if should_retry:
                # 为重试请求生成新的请求ID
                retry_config = original_configs[i].copy()
                retry_config['request_id'] = server.generate_request_id()
                retry_configs.append(retry_config)
                retry_indices.append(i)

        if not retry_configs:
            break  # 没有需要重试的请求

        # 为重试请求重新分配连续的索引（0, 1, 2, ...）
        for j, config in enumerate(retry_configs):
            config['index'] = j

        # 统计重试原因
        timeout_count = sum(1 for i in retry_indices
                            if responses[i] and responses[i].error and responses[i].error_name == 'TimeoutError')
        server_error_count = sum(1 for i in retry_indices
                                 if responses[i] and responses[i].status >= 500)
        network_error_count = sum(1 for i in retry_indices
                                  if responses[i] is None or (responses[i] and responses[i].status == 0))

        retry_reasons = []
        if timeout_count > 0:
            retry_reasons.append(f"{timeout_count}个超时")
        if server_error_count > 0:
            retry_reasons.append(f"{server_error_count}个服务器错误")
        if network_error_count > 0:
            retry_reasons.append(f"{network_error_count}个网络错误")

        print(f"重试第 {retry_count + 1} 次，重试 {len(retry_configs)} 个请求 ({', '.join(retry_reasons)})")

        # 构造并执行重试请求的JS代码
        js_code = _build_batch_js_request_code(retry_configs, f"http://{server.host}:{server.port}")

        try:
            tab.run_js(js_code)
            retry_responses = _wait_for_all_responses(server, retry_configs, server_timeout)

            # 更新原始响应列表中的重试请求
            success_count = 0
            for j, retry_index in enumerate(retry_indices):
                # 检查边界并更新响应
                if j < len(retry_responses) and retry_index < len(responses):
                    if retry_responses[j] is not None:
                        responses[retry_index] = retry_responses[j]
                        # 检查重试是否真正成功（不再是错误状态）
                        if retry_responses[j].is_success():
                            success_count += 1
                else:
                    print(f"警告: 索引越界 - j={j}, retry_index={retry_index}, retry_responses长度={len(retry_responses)}, responses长度={len(responses)}")

            if success_count > 0:
                print(f"重试成功: {success_count}/{len(retry_configs)} 个请求已修复")

        except Exception as e:
            print(f"重试请求时出错: {e}")
            import traceback
            traceback.print_exc()
            break

        retry_count += 1

    return responses


# 便捷方法
def get(tab, url: str, **kwargs) -> Optional[Response]:
    """发送GET请求"""
    return async_request(tab, 'GET', url, **kwargs)


def post(tab, url: str, **kwargs) -> Optional[Response]:
    """发送POST请求"""
    return async_request(tab, 'POST', url, **kwargs)


def put(tab, url: str, **kwargs) -> Optional[Response]:
    """发送PUT请求"""
    return async_request(tab, 'PUT', url, **kwargs)


def delete(tab, url: str, **kwargs) -> Optional[Response]:
    """发送DELETE请求"""
    return async_request(tab, 'DELETE', url, **kwargs)


def patch(tab, url: str, **kwargs) -> Optional[Response]:
    """发送PATCH请求"""
    return async_request(tab, 'PATCH', url, **kwargs)


def batch_request(tab, requests: List[Dict[str, Any]], **kwargs) -> List[Optional[Response]]:
    """
    批量发送异步请求，支持超时和错误状态码重试

    Args:
        tab: DrissionPage的tab对象
        requests: 请求配置列表，每个元素包含method, url等参数
            每个请求可包含的参数:
            - method: 请求方法
            - url: 请求URL
            - headers: 请求头字典
            - data: 请求体数据（JSON格式）
            - form_data: 表单数据（字典格式，自动转换为application/x-www-form-urlencoded）
            - params: URL参数
            - timeout: 请求超时时间
            - force_timeout: 强制超时时间
        **kwargs: 全局配置
            - server_timeout: 等待服务器响应的超时时间（秒）
            - default_timeout: 单个请求的默认超时时间（秒）
            - default_force_timeout: 默认强制超时时间（秒），优先级高于default_timeout
            - retry_timeout: 是否对失败请求进行重试（默认True）
            - max_retries: 最大重试次数（默认1）

    Returns:
        Response对象列表，顺序与输入请求列表一致

    重试条件:
        - 请求超时 (TimeoutError)
        - 服务器错误状态码 (5xx)
        - 网络错误 (状态码为0)
        - 无响应 (None)

    注意:
        - 每个请求的data和form_data参数不能同时使用
        - form_data会自动设置Content-Type为application/x-www-form-urlencoded
    """
    if not requests:
        return []

    server = get_server()
    server_timeout = kwargs.get('server_timeout', 60)
    default_timeout = kwargs.get('default_timeout', 30)
    retry_timeout = kwargs.get('retry_timeout', True)
    max_retries = kwargs.get('max_retries', 1)
    default_force_timeout = kwargs.get('default_force_timeout', None)  # 默认强制超时时间

    # 为每个请求生成配置
    request_configs = []
    for i, req in enumerate(requests):
        # 计算实际超时时间（优先使用强制超时）
        request_timeout = req.get('timeout', default_timeout)
        force_timeout = req.get('force_timeout', default_force_timeout)
        actual_timeout = force_timeout if force_timeout is not None else request_timeout

        # 处理form_data参数
        data = req.get('data')
        form_data = req.get('form_data')
        headers = req.get('headers', {}).copy()

        # 检查data和form_data不能同时使用
        if data is not None and form_data is not None:
            raise ValueError(f"请求 {i}: data和form_data参数不能同时使用，请选择其中一个")

        # 处理form_data参数
        if form_data is not None:
            if not isinstance(form_data, dict):
                raise ValueError(f"请求 {i}: form_data参数必须是字典类型")
            # 将form_data转换为URL编码格式
            data = urlencode(form_data)
            # 自动设置Content-Type
            if 'Content-Type' not in headers:
                headers['Content-Type'] = 'application/x-www-form-urlencoded'

        config = {
            'request_id': server.generate_request_id(),
            'method': req.get('method', 'GET'),
            'url': req['url'],
            'headers': headers,
            'data': data,
            'params': req.get('params', {}),
            'timeout': actual_timeout * 1000,  # 转换为毫秒
            'index': i,
            'original_request': req  # 保存原始请求配置用于重试
        }
        request_configs.append(config)

    # 构造并执行JS代码
    js_code = _build_batch_js_request_code(request_configs, f"http://{server.host}:{server.port}")

    try:
        tab.run_js(js_code)
        responses = _wait_for_all_responses(server, request_configs, server_timeout)

        # 如果启用了超时重试，对超时的请求进行重试
        if retry_timeout and max_retries > 0:
            responses = _retry_timeout_requests(tab, responses, request_configs, server, server_timeout, max_retries)

        return responses
    except Exception as e:
        # print(f"Batch request error: {e}")  # 移除日志输出
        # 为每个请求创建带有请求信息的错误响应
        error_responses = []
        for req in requests:
            request_info = {
                'method': req.get('method', 'GET'),
                'url': req['url'],
                'headers': req.get('headers', {}),
                'data': req.get('data'),
                'form_data': req.get('form_data'),
                'params': req.get('params', {}),
                'timeout': req.get('timeout', default_timeout)
            }
            error_response = Response({'error': True, 'message': str(e), 'status': 0, 'ok': False}, request_info)
            error_responses.append(error_response)
        return error_responses
