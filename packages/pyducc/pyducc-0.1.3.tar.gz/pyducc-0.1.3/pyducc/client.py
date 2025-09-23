import threading
import time
import gzip
import logging
import os
import shutil
import sys
import json
from dataclasses import is_dataclass, fields, dataclass, field, MISSING
from typing import get_origin, Union, get_args, Any, List, Dict, TypeVar, Optional, Type

import requests

from .properties import Properties


class DuccClient:
    """
    DUCC客户端，用于与DUCC服务通信获取配置并管理配置更新
    
    :param application: 应用名
    :param token: 应用token
    :param ns_id: 命名空间名
    :param config_id: 配置名
    :param env: 环境，默认为'pro' 可选值：'dev'、'test'
    :param logger: 自定义日志记录器，默认为None时会创建一个标准日志记录器
    """
    def __init__(
        self,
        application: str,
        token: str,
        ns_id: str,
        config_id: str,
        env: str = 'pro',
        logger: Optional[logging.Logger] = None
    ):
        # 基本配置
        self.app = application
        self.token = token
        self.ns_id = ns_id
        self.config_id = config_id
        self.env = env

        self.logger = logger or self._setup_default_logger()

        self.headers = {
            'application': self.app,
            'token': self.token,
            "client.version": "v1.0.0",
            "User-Agent": "ducc-sdk-python/0.1.3",
            "SDK-Language": "python"
        }
        
        # 初始化配置管理器
        self._config_cache = {}
        self._registered_objects = {}
        self._callbacks = {}
        self._callback_to_keys = {}  # 记录每个回调函数对应的所有key

    def _setup_default_logger(self) -> logging.Logger:
        """设置默认日志记录器"""
        logger = logging.getLogger('ducc')
        logger.setLevel(logging.DEBUG)

        if not logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(asctime)s [%(threadName)-16s] %(levelname)-5s %(module)s - %(message)s',
                datefmt='%y-%m-%d.%H:%M:%S'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def start_polling(
        self,
        profiles: str,
        poll_as_daemon: bool = False,
        polling_timeout_ms: int = 6000,
        name: str = "ducc-config-monitor"
    ) -> threading.Thread:
        """
        启动长轮询获取配置更新，并在成功拉取一次数据后返回
        
        :param profiles: profile名称
        :param poll_as_daemon: 是否将轮询线程设置为daemon，默认False
        :param polling_timeout_ms: 长轮询超时时间，单位毫秒，默认6000
        :param name: 轮询线程名称，默认"ducc-config-monitor"
        :return: 启动的轮询线程对象
        """
        first_poll_success = threading.Event()
        
        def _long_polling():
            """长轮询线程函数"""
            long_polling_api = f'/v1/namespace/{self.ns_id}/config/{self.config_id}/profiles/{profiles}'
            if self.env == 'pro' or self.env == 'pre':
                self.url = 'http://longpolling.ducc.jd.local' + long_polling_api
            else:
                self.url = 'http://test.ducc.jd.local' + long_polling_api

            headers = {
                'application': self.app,
                'token': self.token,
                'Accept': 'application/json;charset=UTF-8',
                'If-Modified-Since': '0'
            }

            timeout = (3, polling_timeout_ms * 1.2 / 1000)
            last_modified = -1

            while True:
                try:
                    t_start = time.time()
                    self.logger.debug(f'DUCC配置变更, 开始长轮询, 轮询时间: {polling_timeout_ms * 0.001}s', )

                    res = requests.get(
                        self.url,
                        params={
                            'longPolling': polling_timeout_ms
                        },
                        headers=headers,
                        timeout=timeout
                    )

                    if res.status_code == 200:
                        res_body = res.json()
                        real_status = res_body.get("status")

                        if real_status != 200:
                            self.logger.error(f"DUCC配置变更, 调用DUCC长轮询接口失败，status={real_status}, message={res_body.get('message')}, url={self.url}")
                            time.sleep(timeout[1])
                            continue

                        input_text = res.text
                        self.logger.debug(f"DUCC配置变更, 长轮询返回200, Last-Modified={res.headers['Last-Modified']}" )

                        headers['If-Modified-Since'] = res.headers['Last-Modified']
                        self.logger.debug(f"DUCC配置变更, 读取ducc更新配置用时：{(time.time() - t_start)*1000:.2f}毫秒")

                        config_type = res.headers.get("Laf-Config-Type", "")
                        if config_type == "propertiesFile":
                            for item in res_body.get("data", []):
                                if item.get("key") == "data.release.all":
                                    download_url = item.get("value", "")
                                    text = self._get_large_kv(download_url)
                                    if text:
                                        self.logger.debug("DUCC配置变更, 大k，v模式加载")
                                        input_text = text
                                    else:
                                        self.logger.error(f"DUCC配置变更, 获取解析大KV失败，url = {download_url}" )
                                        input_text = ""

                            if not input_text:
                                continue

                        if last_modified != headers['If-Modified-Since']:
                            self._process_config_update(input_text)
                            self.logger.debug(f"DUCC配置变更, 更新配置完成用时：{(time.time() - t_start)*1000:.2f}毫秒,版本 {last_modified} -> { headers['If-Modified-Since']}")
                            last_modified = headers['If-Modified-Since']
                            
                            # 标记首次成功拉取数据
                            if not first_poll_success.is_set():
                                self.logger.info(f"DUCC配置变更, 首次成功拉取数据,env:{self.env}")
                                first_poll_success.set()
                        else:
                            self.logger.debug("DUCC配置变更, 前后版本相同不用更新,版本号{}", last_modified)

                    elif res.status_code == 304:
                        self.logger.debug(
                            f'DUCC配置变更, 长轮询返回304，继续... {(time.time() - t_start):.2f}s',

                        )
                        time.sleep(timeout[1])
                        continue
                except requests.exceptions.ConnectionError as e:
                    self.logger.error(f"DUCC配置变更, 长轮询过程中连接异常, 请检查网络或服务 url: {self.url}")
                    time.sleep(timeout[1])
                except requests.exceptions.Timeout as e:
                    self.logger.error(f"DUCC配置变更, 长轮询过程中请求超时,请修改配置或检查网络 url: {self.url} 当前超时时间 {polling_timeout_ms}ms")
                    time.sleep(timeout[1])
                except Exception as e:
                    self.logger.error(f"DUCC配置变更, 长轮询过程中发生异常,等待下次重试, url: {self.url}: {str(e)}")
                    time.sleep(timeout[1])

        thread = threading.Thread(target=_long_polling, name=name, daemon=poll_as_daemon)
        thread.start()
        
        # 等待首次成功拉取数据
        self.logger.info(f"等待首次成功拉取DUCC配置,env:{self.env}")
        first_poll_success.wait()
        self.logger.info(f"首次DUCC配置拉取成功,env:{self.env}，继续执行")
        
        return thread

    def _get_large_kv(self, download_url: str, retry_count: int = 1, max_retries: int = 3) -> str:
        """
        获取并解析大文件模式的配置
        
        :param download_url: 下载URL
        :param retry_count: 当前重试次数
        :param max_retries: 最大重试次数
        :return: 解析后的配置文本
        """
        if retry_count > max_retries:
            self.logger.error(f"DUCC配置变更, ducc下载解析超过{max_retries}次数后仍报错" )
            return ""

        process_id = os.getpid()
        thread_id = threading.current_thread().ident
        local_gzip_path = f"all_{process_id}_{thread_id}.properties.gz"
        local_properties_path = f"all_{process_id}_{thread_id}.properties"

        try:
            response = requests.get(download_url, stream=True)
            if response.status_code != 200:
                self.logger.error(f"DUCC配置变更, 下载文件失败，状态码: {response.status_code}" )
                return self._get_large_kv(download_url, retry_count + 1, max_retries)

            with open(local_gzip_path, 'wb+') as f:
                f.write(response.content)
            self.logger.debug(f"DUCC配置变更, 成功下载gzip文件: {local_gzip_path}" )

            try:
                with gzip.open(local_gzip_path, 'rb') as f_in, open(local_properties_path, 'wb+') as f_out:
                    shutil.copyfileobj(f_in, f_out)
                self.logger.debug(f"DUCC配置变更, 成功解压文件:{local_properties_path}", )
            except Exception:
                self.logger.exception(f"DUCC配置变更, 解压文件出错，进行第{retry_count + 1}次下载")
                return self._get_large_kv(download_url, retry_count + 1, max_retries)

            properties = []
            configs = Properties()

            with open(local_properties_path, 'rb') as config_file:
                configs.load(config_file)
                for item in configs.items():
                    properties.append({"key": item[0], "value": item[1].data})

            os.remove(local_gzip_path)
            os.remove(local_properties_path)
            self.logger.debug("DUCC配置变更, 已删除临时gzip和properties文件")

            # 构造结果
            if properties:
                result_dict = {
                    "status": 200,
                    "code": 200,
                    "data": properties
                }
                return json.dumps(result_dict)

            return ""

        except Exception:
            self.logger.exception(f"DUCC配置变更, 下载解析大文件错误url = {download_url}")
            return self._get_large_kv(download_url, retry_count + 1, max_retries)

    def _process_config_update(self, result_txt: str) -> None:
        """
        处理配置更新
        
        :param result_txt: 配置内容文本
        """
        try:
            res = json.loads(result_txt)
            code = res.get("code")
            status = res.get("status")

            if code != 200:
                self.logger.error(f"DUCC配置变更回调#返回失败.code={code},status={status}")
                return

            data_list = res.get("data", [])
            self.logger.info(f"DUCC配置变更回调#data_list={data_list}")

            if not data_list:
                self.logger.warning("DUCC配置变更回调#DUCC配置变更回调数据为空")
                return

            # 初始化已调用的回调函数集合，用于确保同一批次更新中同一个回调函数只被调用一次
            setattr(self, '_called_callbacks', set())
            
            # 更新配置缓存并通知注册的对象
            for item in data_list:
                key = item.get("key")
                value = item.get("value")

                if key and value is not None:
                    try:
                        parsed_value = json.loads(value)
                    except (json.JSONDecodeError, TypeError):
                        parsed_value = value
                    self._update_config(key, parsed_value)
            
            # 清理已调用的回调函数集合
            delattr(self, '_called_callbacks')

        except Exception as e:
            self.logger.exception("DUCC配置变更回调#处理DUCC配置回调时出错", e)

    def register_config(self, config_instance: Any) -> None:
        """
        注册配置类实例
        
        :param config_instance: 要注册的配置类实例
        """
        if not is_dataclass(config_instance):
            self.logger.warning(f"DUCC配置变更, 只能注册dataclass实例，忽略: {type(config_instance).__name__}" )
            return

        self._register_dataclass(config_instance)

    def register_callback(self, keys, callback: callable) -> None:
        """
        注册配置变更回调函数，可以为一个回调函数指定多个key，任意一个key变化都会触发回调

        :param keys: 配置键或配置键列表/元组
        :param callback: 回调函数，接收两个参数(key, new_value)
        """
        if not callable(callback):
            self.logger.warning(f"DUCC配置变更, 回调必须是可调用对象: {callback}")
            return

        # 将单个key转换为列表
        if isinstance(keys, str):
            keys = [keys]
        
        # 记录回调函数对应的所有key
        if callback not in self._callback_to_keys:
            self._callback_to_keys[callback] = set()
        
        # 为每个key注册回调函数
        for key in keys:
            if key not in self._callbacks:
                self._callbacks[key] = []

            if callback not in self._callbacks[key]:
                self._callbacks[key].append(callback)
                self._callback_to_keys[callback].add(key)
                self.logger.debug(f"DUCC配置变更, 已注册回调函数: {key} --> {callback.__name__}")
            else:
                self.logger.debug(f"DUCC配置变更, 回调函数已存在: {key} --> {callback.__name__}")

    def _register_dataclass(self, instance: Any) -> None:
        """
        注册dataclass实例及其被DuccValue注解的字段
        
        :param instance: 数据类实例
        """
        for field_info in fields(instance.__class__):
            if hasattr(field_info, 'metadata') and 'ducc_value' in field_info.metadata:
                ducc_value = field_info.metadata['ducc_value']
                key = ducc_value.key
                default_value = ducc_value.default_value

                if key not in self._registered_objects:
                    self._registered_objects[key] = []
                self._registered_objects[key].append((instance, field_info.name))

                if default_value is not None:
                    setattr(instance, field_info.name, default_value)

                if key in self._config_cache:
                    self._update_field_value(instance, field_info.name, self._config_cache[key])

        self.logger.debug(f"DUCC配置变更, 已注册配置类: {type(instance).__name__}")

    def _update_config(self, key: str, value: Any) -> None:
        """
        更新配置值，并自动更新所有注册的对象字段
        只有当值发生变化时才进行更新
        
        :param key: 配置键
        :param value: 配置值
        """
        old_value = None
        if key not in self._config_cache:
            self._config_cache[key] = value
            self.logger.info(f"DUCC配置变更回调#新增操作.key={key},新值={value}")
            value_changed = True
        else:
            old_value = self._config_cache[key]
            try:
                if isinstance(value, (dict, list)) or isinstance(old_value, (dict, list)):
                    value_changed = json.dumps(value, sort_keys=True) != json.dumps(old_value, sort_keys=True)
                else:
                    value_changed = value != old_value
            except (TypeError, ValueError):
                self.logger.warning(f"DUCC配置变更回调#DUCC无法比较值:{key}" )
                value_changed = True

            if value_changed:
                self._config_cache[key] = value
                self.logger.info(f"DUCC配置变更回调#更新操作.key={key},旧值={old_value},新值={value}")

        if value_changed:
            if key in self._registered_objects:
                for obj, field_name in self._registered_objects[key]:
                    self._update_field_value(obj, field_name, value)
            
            # 触发注册的回调函数
            if key in self._callbacks and self._callbacks[key]:
                # 获取当前批次已调用的回调函数集合
                called_callbacks = getattr(self, '_called_callbacks', set())
                
                for callback in self._callbacks[key]:
                    # 确保同一批次中同一个回调函数只被调用一次
                    if callback not in called_callbacks:
                        try:
                            self.logger.debug(f"DUCC配置变更,执行回调函数: {callback.__name__}")
                            callback(key,old_value,value)
                            called_callbacks.add(callback)
                            self.logger.debug(f"DUCC配置变更,回调函数 {callback.__name__} 执行成功")
                        except Exception as e:
                            self.logger.error(f"DUCC配置变更,执行回调函数时出错: {e}")
                
                # 更新已调用的回调函数集合
                setattr(self, '_called_callbacks', called_callbacks)


    def _update_field_value(self, obj: object, field_name: str, value: Any) -> None:
        """
        更新对象的字段值
        
        :param obj: 目标对象
        :param field_name: 字段名
        :param value: 新值
        """
        if not hasattr(obj, field_name):
            self.logger.warning(f"DUCC配置变更, 对象 {type(obj).__name__} 没有字段 {field_name}" )
            return

        field_type = None
        if is_dataclass(obj.__class__):
            for f in fields(obj.__class__):
                if f.name == field_name:
                    field_type = f.type
                    break

        try:
            if field_type is not None:
                # 使用convert_to_dataclass转换值
                converted_value = convert_to_dataclass(value, field_type)
                setattr(obj, field_name, converted_value)
            else:
                setattr(obj, field_name, value)
        except Exception as e:
            self.logger.error(f"DUCC配置变更, 更新字段 {field_name} 值 {value} 失败: {e}")

    def get_config(self, key: str) -> Any:
        """
        获取配置值
        
        :param key: 配置键
        :return: 配置值，如果不存在则返回None
        """
        return self._config_cache.get(key)

    def get_all_configs(self) -> Dict[str, Any]:
        """
        获取所有配置
        
        :return: 所有配置的副本
        """
        return self._config_cache.copy()


# 类型变量定义，用于泛型支持
T = TypeVar('T')


def convert_to_dataclass(data: Any, target_class: Type[T]) -> T:
    """
    递归将字典/列表转换为目标数据类
    
    :param data: 要转换的数据
    :param target_class: 目标数据类类型
    :return: 转换后的数据类实例
    """
    if data is None:
        return None

    # 处理列表类型
    origin = get_origin(target_class)
    if origin is list:
        element_type = get_args(target_class)[0]
        return [convert_to_dataclass(item, element_type) for item in data]

    # 处理字典类型
    if origin is dict:
        key_type, value_type = get_args(target_class)
        return {k: convert_to_dataclass(v, value_type) for k, v in data.items()}

    # 处理数据类
    if is_dataclass(target_class):
        if not isinstance(data, dict):
            return data

        field_definitions = {f.name: f for f in fields(target_class)}
        kwargs = {}

        for name, field_def in field_definitions.items():
            if name not in data:
                # 使用默认值
                if field_def.default is not MISSING:
                    kwargs[name] = field_def.default
                elif field_def.default_factory is not MISSING:
                    kwargs[name] = field_def.default_factory()
                continue

            raw_value = data.get(name)
            field_type = field_def.type

            # 处理Optional类型
            if get_origin(field_type) is Union and type(None) in get_args(field_type):
                non_none_types = [t for t in get_args(field_type) if t is not type(None)]
                if len(non_none_types) == 1:
                    actual_type = non_none_types[0]
                    kwargs[name] = convert_to_dataclass(raw_value, actual_type)
                else:
                    kwargs[name] = raw_value
            else:
                kwargs[name] = convert_to_dataclass(raw_value, field_type)

        return target_class(**kwargs)

    # 基础类型直接返回
    return data


class DuccValue:
    """
    DUCC配置值注解，用于标记数据类字段与DUCC配置的映射关系
    
    :param key: DUCC配置的key
    :param default_value: 默认值
    """
    def __init__(self, key: str, default_value: Any = None):
        self.key = key
        self.default_value = default_value


def ducc_field(key: str, default_value: Any = None):
    """
    DUCC配置字段装饰器，简化配置字段定义
    
    :param key: DUCC配置的key
    :param default_value: 默认值
    :return: 字段元数据
    
    使用示例:
    ```python
    @dataclass
    class MyConfig:
        api_url: str = ducc_field("api.url", "https://default-api.com")
        timeout: int = ducc_field("api.timeout", 30)
    ```
    """
    if default_value is None:
        return field(metadata={'ducc_value': DuccValue(key=key, default_value=default_value)})
    
    # 对于可变对象，使用default_factory
    if isinstance(default_value, (dict, list)):
        return field(
            default_factory=lambda: default_value.copy() if hasattr(default_value, 'copy') else type(default_value)(),
            metadata={'ducc_value': DuccValue(key=key, default_value=default_value)}
        )
    
    # 对于不可变对象，使用default
    return field(
        default=default_value,
        metadata={'ducc_value': DuccValue(key=key, default_value=default_value)}
    )