# pyducc - Python DUCC Client
# 用于与DUCC服务通信获取配置并管理配置更新的客户端

from .client import DuccClient, DuccValue, ducc_field, convert_to_dataclass

__version__ = "0.1.3"
__all__ = [
    "DuccClient",
    "DuccValue",
    "ducc_field",
    "convert_to_dataclass"
]