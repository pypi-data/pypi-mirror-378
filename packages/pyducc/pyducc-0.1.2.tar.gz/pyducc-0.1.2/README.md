# PyDUCC

PyDUCC是一个Python客户端库，用于与DUCC（分布式统一配置中心）服务通信，获取配置并管理配置更新。

## 特性

- 支持从DUCC服务获取配置
- 支持配置自动更新（长轮询）
- 支持回调函数，当特定配置更新时，自动调用回调函数
- 支持数据类映射，支持级联配置（使用Python dataclass）

## 安装

```bash
pip install pyducc
```

## 快速开始

### 基本用法

```python
from pyducc import DuccClient

# 创建配置客户端
ducc_client = DuccClient(
    application='your-app-name',
    token='your-token',
    ns_id='your-namespace',
    config_id='your-config-id',
    env='pro'  # 可选值：'dev', 'test', 'pre', 'pro'
)

# 获取配置
config_value = ducc_client.get_config("your.config.key")
print(f"配置值: {config_value}")

# 获取所有配置
all_configs = ducc_client.get_all_configs()
print(f"所有配置: {all_configs}")
```

### 使用数据类
- 使用`@dataclass`装饰器定义数据类，并使用`ducc_field`装饰器标记需要从DUCC获取的配置项
- 创建配置客户端DuccClient
- 将自定义数据类注册到DuccClient中
- 开启长轮训配置监听（配置变更后SDK会自动更新自定义数据类的值）

```python
from dataclasses import dataclass
import time
from typing import List

from pyducc import ducc_field, DuccClient

@dataclass
class ConfigItem:
    """被主配置类引用的配置项类"""
    model: str
    timeout: int
    top_p: float

@dataclass
class DuccConfig:
    """定义主配置类"""
    # 配置列表，自定义配置类
    test_configs: List[ConfigItem] = ducc_field(key="test_config",default_value=[])
    # 配置bool变量
    search_mock: bool = ducc_field(key="vectorSearchMock",default_value=False)

# 创建全局配置实例
DUCC_CONFIG = DuccConfig()

# 初始化Ducc接入
def ducc_init():
    # 创建配置客户端
    ducc_client = DuccClient(
        application='your-app-name',
        token='your-token',
        ns_id='your-namespace',
        config_id='your-config-id',
        env='test'
    )
    # 注册配置类
    ducc_client.register_config(DUCC_CONFIG)
    # 启动配置轮询
    ducc_client.start_polling('test', poll_as_daemon=True, polling_timeout_ms=6000)

if __name__ == '__main__':
    # 在程序启动时进行Ducc初始化
    ducc_init()
    # 监控配置变化
    try:
        while True:
            print(f"--- 当前配置状态 ---")
            print(f"test_configs: {DUCC_CONFIG.test_configs}")
            print(f"search_mock: {DUCC_CONFIG.search_mock}")
            time.sleep(5)
    except KeyboardInterrupt:
        print("程序已终止")
```

## API参考

### DuccClient

```python
DuccClient(
    application: str,
    token: str,
    ns_id: str,
    config_id: str,
    env: str = 'pro',
    logger: Optional[logging.Logger] = None
)
```

#### 参数

- `application`: 应用名
- `token`: 应用token
- `ns_id`: 命名空间名
- `config_id`: 配置名
- `env`: 环境，默认为'pro' 可选值：'dev'、'test'、'pre'、'pro'
- `logger`: 自定义日志记录器，默认为None时会创建一个标准日志记录器

#### 方法

- `start_polling(profiles, poll_as_daemon=False, polling_timeout_ms=6000, name="ducc-config-monitor")`: 启动长轮询获取配置更新
- `register_config(config_instance)`: 注册配置类实例，一般为全局变量
- `get_config(key)`: 获取配置值
- `get_all_configs()`: 获取所有配置

### ducc_field

```python
ducc_field(key: str, default_value: Any = None)
```

用于在数据类中定义DUCC配置字段的装饰器。

#### 参数

- `key`: DUCC配置的key
- `default_value`: 默认值

## 许可证

MIT