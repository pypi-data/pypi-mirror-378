# Pika MQ Consumer

[![PyPI version](https://badge.fury.io/py/pika-mq-consumer.svg)](https://badge.fury.io/py/pika-mq-consumer)
[![Python version](https://img.shields.io/pypi/pyversions/pika-mq-consumer.svg)](https://pypi.org/project/pika-mq-consumer/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

🚀 **简化的RabbitMQ消费者包装器** - 提供类似npm包的简洁API，让您轻松消费RabbitMQ消息！现在还包含文件上传和HTTP客户端功能！

## ✨ 特性

### 🐰 RabbitMQ消费者
- 🎯 **简洁API** - 类似npm包的使用体验
- 🔄 **自动重连** - 内置重连机制，保证服务稳定性
- 🎨 **装饰器模式** - 优雅的消息处理器注册方式
- 📦 **JSON支持** - 自动JSON序列化/反序列化
- 🛡️ **错误处理** - 完善的异常处理和重试机制
- 🧵 **多线程支持** - 支持后台线程消费
- ⚙️ **灵活配置** - 丰富的配置选项

### 📤 文件上传服务
- 🌐 **自动获取上传地址** - 动态获取上传服务器
- 🔄 **重试机制** - 上传失败自动重试
- 📁 **多格式支持** - 支持图片、视频等多种文件
- 🎯 **简洁输出** - 只显示关键信息（成功地址或错误信息）

### 🌐 HTTP客户端
- 🔄 **自动重试** - POST请求失败自动重试，支持指数退避
- 📝 **URL编码格式** - 使用application/x-www-form-urlencoded格式
- 🛡️ **错误处理** - 完善的异常捕获和处理
- 🎯 **简洁API** - 只需3个参数：url、data、retries

## 🚀 快速开始

### 安装

```bash
pip install pika-mq-consumer
```

### 基础用法

```python
import asyncio
import os
from pika_mq_consumer import MQConsumer

async def handle_message(content):
    """处理消息的函数"""
    print(f"收到消息: {content}")
    # 在这里添加您的业务逻辑
    return "success"

async def main():
    # 完全参考amqplib-init的配置方式
    await MQConsumer.init({
        'channel_name': 'my-queue',                    # 队列名称
        'prefetch': 1,                                 # 并发控制
        'delay': 100,                                  # 延迟ACK (毫秒)
        'amqp_auto_link': os.getenv('RABBITMQ_CONFIG_URL'),  # 自动获取连接配置
        'callback': handle_message,                    # 消息处理函数
        'finish': lambda: print("🎉 消费者启动完成！"),
    })

if __name__ == '__main__':
    # 设置环境变量
    # export RABBITMQ_CONFIG_URL='https://your-api.com/config'
    asyncio.run(main())
    
    # 保持程序运行
    while True:
        time.sleep(1)
```

### 高级用法

```python
import asyncio
import os
import time
from pika_mq_consumer import MQConsumer

async def process_order(content):
    """处理订单消息"""
    order_id = content.get('order_id')
    print(f"🛒 处理订单: {order_id}")
    
    # 模拟订单处理逻辑
    await asyncio.sleep(2)
    
    print(f"✅ 订单处理完成: {order_id}")
    return "success"

def check_system_status():
    """检查系统状态，决定是否可以重启"""
    # 检查数据库连接、外部服务状态等
    return True

def init_hook(context):
    """初始化钩子函数"""
    print("🔗 MQ连接已建立")
    # 可以在这里执行初始化操作

async def start_consumer():
    await MQConsumer.init({
        'channel_name': os.getenv('QUEUE_NAME', 'order-queue'),
        'prefetch': 2,                                    # 并发处理2个消息
        'delay': 200,                                     # 延迟200ms ACK
        'amqp_auto_link': os.getenv('RABBITMQ_CONFIG_URL'),  # 自动获取配置
        'amqp_link': os.getenv('RABBITMQ_URL', ''),       # 备用连接地址
        'heartbeat': 10,                                  # 心跳间隔
        'timeout': 5000,                                  # 连接超时
        'auto_reload': 60000,                             # 自动重载检查间隔
        'pm_id': os.getenv('PM2_ID', '0'),               # PM2进程ID
        'callback': process_order,                        # 消息处理函数
        'query_hook': check_system_status,                # 系统状态检查
        'init_hook': init_hook,                          # 初始化钩子
        'finish': lambda: print("🎉 消费者启动完成！"),
    })

if __name__ == '__main__':
    asyncio.run(start_consumer())
    
    # 保持程序运行
    while True:
        time.sleep(1)
```

### 环境变量配置

在使用前，请设置必要的环境变量：

```bash
# 必需：RabbitMQ配置API地址
export RABBITMQ_CONFIG_URL='https://your-api.com/config/getRabbitMqQueryConfig.html?key=your-key'

# 可选：备用连接地址
export RABBITMQ_URL='amqp://username:password@host:port/'

# 可选：队列名称
export QUEUE_NAME='your-queue-name'

# 可选：PM2进程ID（用于自动重载）
export PM2_ID='0'

# 运行程序
python your_consumer.py
```

## 📤 文件上传功能

### 基础用法

```python
from pika_mq_consumer import upload_file, upload_image, upload_video

# 1. 上传图片
result = upload_image('path/to/image.jpg')
if result and result.get('code') == 1:
    print(f"✅ {result['info']}")  # 输出: ✅ https://your-domain.com/path/to/uploaded/image.jpg
else:
    print(f"❌ {result.get('info', '上传失败')}")

# 2. 上传视频
result = upload_video('path/to/video.mp4')
if result and result.get('code') == 1:
    print(f"✅ {result['info']}")
else:
    print(f"❌ {result.get('info', '上传失败')}")

# 3. 通用文件上传
result = upload_file('path/to/any_file.pdf')
if result and result.get('code') == 1:
    print(f"✅ {result['info']}")
else:
    print(f"❌ {result.get('info', '上传失败')}")
```

### 自定义上传器

```python
from pika_mq_consumer import FileUploader

# 创建自定义上传器
uploader = FileUploader(
    upload_host_api='https://your-api.com/getUploadHost.html',
    max_retries=5,
    timeout=60,
    verify_ssl=False
)

# 使用自定义上传器
result = uploader.upload_file('my_file.jpg', custom_filename='new_name.jpg')
```

## 🌐 HTTP客户端功能

### 简洁的POST请求

```python
from pika_mq_consumer import http_post

# 基础用法
result = http_post(
    url='https://api.example.com/submit',
    data={'key': 'value', 'name': 'test'},
    retries=3
)

if result:
    print(f"响应: {result}")

# 错误处理
if result and result.get('success') == False:
    print(f"请求失败: {result.get('error')}")
else:
    print("请求成功!")
```

### 使用示例

```python
from pika_mq_consumer import http_post

# 提交表单数据
form_data = {
    'username': 'john',
    'password': '123456',
    'action': 'login'
}

result = http_post(
    url='https://your-api.com/login',
    data=form_data,
    retries=5  # 重试5次
)

# 检查结果
if result:
    if result.get('success') != False:
        print("登录成功!")
    else:
        print(f"登录失败: {result.get('error')}")
```

## 📚 API文档

### 文件上传 API

#### upload_file(file_path, upload_host=None)

通用文件上传函数。

**参数：**
- `file_path` (str): 要上传的本地文件路径
- `upload_host` (str, optional): 自定义上传服务器地址，不提供则自动获取

**返回值：**
- `dict`: 上传结果字典
  - `code` (int): 响应码，1表示成功，0表示失败
  - `info` (str): 成功时返回文件URL，失败时返回错误信息
  - `msg` (str): 响应消息
  - `file_info` (dict): 文件信息（大小、类型等）
  - `upload_time` (float): 上传时间戳

**示例：**
```python
from pika_mq_consumer import upload_file

result = upload_file('document.pdf')
if result and result.get('code') == 1:
    print(f"✅ {result['info']}")  # 文件URL
else:
    print(f"❌ {result.get('info', '上传失败')}")
```

#### upload_image(file_path, upload_host=None)

图片文件上传函数（等同于upload_file）。

#### upload_video(file_path, upload_host=None)

视频文件上传函数（等同于upload_file）。

#### FileUploader 类

自定义文件上传器，提供更多配置选项。

**初始化参数：**
- `upload_host_api` (str): 获取上传地址的API URL
- `max_retries` (int): 最大重试次数，默认3
- `timeout` (int): 请求超时时间（秒），默认30
- `verify_ssl` (bool): 是否验证SSL证书，默认False

**方法：**
- `upload_file(file_path, upload_host=None, custom_filename=None)`: 上传文件

**示例：**
```python
from pika_mq_consumer import FileUploader

uploader = FileUploader(
    upload_host_api='https://your-api.com/getUploadHost.html',
    max_retries=5,
    timeout=60
)

result = uploader.upload_file('image.jpg', custom_filename='new_name.jpg')
```

### HTTP客户端 API

#### http_post(url, data=None, retries=3)

发送POST请求，使用application/x-www-form-urlencoded格式。

**参数：**
- `url` (str): 请求URL
- `data` (dict, optional): 表单数据字典
- `retries` (int): 重试次数，默认3次

**返回值：**
- `dict`: 响应结果字典
  - 成功时：返回JSON响应内容
  - 失败时：包含`success: False`和`error`字段

**特性：**
- 自动重试（指数退避）
- 30秒超时
- 不验证SSL证书
- 自动设置Content-Type为application/x-www-form-urlencoded

**示例：**
```python
from pika_mq_consumer import http_post

# 基础用法
result = http_post(
    url='https://api.example.com/login',
    data={'username': 'admin', 'password': '123456'},
    retries=3
)

if result:
    if result.get('success') != False:
        print("请求成功")
        print(f"响应: {result}")
    else:
        print(f"请求失败: {result.get('error')}")
```

### MQConsumer.init() 方法

完全参考 amqplib-init 的配置方式：

#### 配置参数

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `channel_name` | str | 'node-test-channel' | 队列名称 |
| `prefetch` | int | 1 | 并发处理消息数量 |
| `delay` | int | 0 | 延迟ACK时间（毫秒） |
| `callback` | callable | - | 消息处理函数 |
| `finish` | callable | - | 初始化完成回调 |
| `amqp_auto_link` | str | '' | 自动获取连接配置的API地址 |
| `amqp_link` | str | '' | 备用RabbitMQ连接地址 |
| `heartbeat` | int | 5 | 心跳间隔（秒） |
| `timeout` | int | 2000 | 连接超时时间（毫秒） |
| `auto_reload` | int | 0 | 自动重载检查间隔（毫秒，0表示禁用） |
| `pm_id` | str | '0' | PM2进程ID |
| `query_hook` | callable | - | 查询钩子函数 |
| `init_hook` | callable | - | 初始化钩子函数 |

#### 使用方式

##### 基本配置

```python
await MQConsumer.init({
    'channel_name': 'my-queue',
    'prefetch': 1,
    'callback': your_message_handler,
    'amqp_auto_link': os.getenv('RABBITMQ_CONFIG_URL'),
})
```

##### 完整配置

```python
await MQConsumer.init({
    'channel_name': 'production-queue',
    'prefetch': 5,                                    # 并发处理5个消息
    'delay': 100,                                     # 延迟100ms ACK
    'amqp_auto_link': os.getenv('RABBITMQ_CONFIG_URL'),  # 主要配置来源
    'amqp_link': os.getenv('RABBITMQ_URL'),           # 备用连接
    'heartbeat': 10,                                  # 10秒心跳
    'timeout': 5000,                                  # 5秒超时
    'auto_reload': 30000,                             # 30秒检查重载
    'pm_id': '0',                                     # PM2进程ID
    'callback': process_message,                      # 消息处理函数
    'finish': lambda: print("启动完成"),               # 完成回调
    'query_hook': check_can_reload,                   # 重载检查函数
    'init_hook': on_connection_ready,                 # 连接就绪回调
})
```

### 消息处理器函数

消息处理器函数只接收一个参数：

**content**: 消息内容
- 自动JSON解析（如果是JSON格式）
- 原始字符串（如果不是JSON）

```python
async def handle_message(content):
    """
    处理消息函数
    
    Args:
        content: 消息内容（dict 或 str）
        
    Returns:
        str: 处理结果（可选）
    """
    print(f"收到消息: {content}")
    
    # 处理业务逻辑
    if isinstance(content, dict):
        task_type = content.get('type')
        if task_type == 'order':
            await process_order(content)
        elif task_type == 'notification':
            await send_notification(content)
    
    return "success"  # 可选返回值
```

**异常处理：**
- 函数正常返回：消息ACK
- 抛出异常：消息NACK并重新入队

## 🛠️ 开发

### 本地开发环境

```bash
# 克隆项目
git clone https://github.com/yourusername/pika-mq-consumer.git
cd pika-mq-consumer

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码格式化
black .

# 类型检查
mypy pika_mq_consumer
```

### 构建和发布

```bash
# 构建包
python -m build

# 发布到测试PyPI
python -m twine upload --repository testpypi dist/*

# 发布到正式PyPI
python -m twine upload dist/*
```

## 🔧 配置示例

### 连接配置

```python
# 基本连接
consumer = MQConsumer(
    host='rabbitmq.example.com',
    port=5672,
    username='myuser',
    password='mypassword',
    virtual_host='/production'
)

# SSL连接
consumer = MQConsumer(
    host='secure-rabbitmq.example.com',
    port=5671,
    username='myuser',
    password='mypassword',
    ssl_options={
        'ssl_version': ssl.PROTOCOL_TLS,
        'cert_reqs': ssl.CERT_REQUIRED,
        'ca_certs': '/path/to/ca_certificate.pem',
        'certfile': '/path/to/client_certificate.pem',
        'keyfile': '/path/to/client_key.pem',
    }
)
```

### 队列配置

```python
# 持久化队列，手动确认
@consumer.queue('important_queue', 
                durable=True, 
                auto_ack=False, 
                prefetch_count=1)
def handle_important(body, properties):
    # 重要消息处理
    pass

# 临时队列，自动确认
@consumer.queue('temp_queue', 
                durable=False, 
                auto_delete=True, 
                auto_ack=True,
                prefetch_count=100)
def handle_temp(body, properties):
    # 临时消息处理
    pass
```

## 🤝 贡献

欢迎贡献代码！请遵循以下步骤：

1. Fork本项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🆘 支持

- 📖 [文档](https://pika-mq-consumer.readthedocs.io/)
- 🐛 [问题报告](https://github.com/yourusername/pika-mq-consumer/issues)
- 💬 [讨论](https://github.com/yourusername/pika-mq-consumer/discussions)

## 📝 更新日志

### v1.1.0 (2025-09-21)
- 🎉 新增功能
- 📤 **文件上传服务** - 支持图片、视频等文件上传
  - 自动获取上传地址
  - 重试机制和错误处理
  - 简洁的日志输出
- 🌐 **HTTP客户端** - 简化的POST请求功能
  - application/x-www-form-urlencoded格式
  - 自动重试和指数退避
  - 只需3个参数：url、data、retries
- 🎯 **日志级别控制** - 可配置的日志输出级别
- 🔧 **代码优化** - 移除冗余功能，专注核心需求

### v1.0.0 (2024-09-21)
- 🎉 首次发布
- ✨ 基础消费者功能
- 🔄 自动重连机制
- 🎨 装饰器API
- 📦 JSON支持
- 🧵 多线程支持
