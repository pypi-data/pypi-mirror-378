"""
Pika MQ Consumer - 简化的RabbitMQ消费者包装器

这个包提供了一个简洁的接口来消费RabbitMQ消息，基于pika库构建。
让您可以像使用npm包一样轻松集成MQ消费功能。

作者: 您的名字
版本: 1.0.0
许可: MIT
"""

from .consumer import MQConsumer
from .exceptions import MQConsumerError, ConnectionError, ConsumerError

__version__ = "1.0.0"
__author__ = "您的名字"
__email__ = "your.email@example.com"

# 导出主要类和异常
__all__ = [
    'MQConsumer',
    'MQConsumerError', 
    'ConnectionError',
    'ConsumerError'
]
