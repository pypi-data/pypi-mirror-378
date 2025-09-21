"""
Pika MQ Consumer - 简化的RabbitMQ消费者包装器

这个包提供了一个简洁的接口来消费RabbitMQ消息，基于pika库构建。
让您可以像使用npm包一样轻松集成MQ消费功能。
现在还包含统一的文件上传服务和HTTP客户端。

作者: pika-mq-consumer
版本: 1.1.1
许可: MIT
"""

from .consumer import MQConsumer
from .exceptions import MQConsumerError, ConnectionError, ConsumerError
from .uploader import FileUploader, upload_image, upload_video, upload_file
from .http_client import http_post

__version__ = "1.1.1"
__author__ = "pika-mq-consumer"
__email__ = "iyahe29@gmail.com"

# 导出主要类和异常
__all__ = [
    # MQ消费者
    'MQConsumer',
    'MQConsumerError',
    'ConnectionError',
    'ConsumerError',

    # 文件上传
    'FileUploader',
    'upload_image',
    'upload_video',
    'upload_file',

    # HTTP客户端
    'http_post'
]
