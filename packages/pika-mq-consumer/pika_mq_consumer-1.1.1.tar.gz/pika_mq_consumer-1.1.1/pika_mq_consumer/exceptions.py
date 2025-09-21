"""
自定义异常类模块

定义了MQ消费者相关的异常类型，便于错误处理和调试。
"""


class MQConsumerError(Exception):
    """MQ消费者基础异常类"""
    
    def __init__(self, message: str, error_code: str = None):
        """
        初始化异常
        
        Args:
            message (str): 错误消息
            error_code (str): 错误代码，用于程序化处理
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
    
    def __str__(self):
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class ConnectionError(MQConsumerError):
    """连接相关异常"""
    
    def __init__(self, message: str, host: str = None, port: int = None):
        """
        初始化连接异常
        
        Args:
            message (str): 错误消息
            host (str): 连接主机
            port (int): 连接端口
        """
        super().__init__(message, "CONNECTION_ERROR")
        self.host = host
        self.port = port


class ConsumerError(MQConsumerError):
    """消费者相关异常"""
    
    def __init__(self, message: str, queue_name: str = None):
        """
        初始化消费者异常
        
        Args:
            message (str): 错误消息
            queue_name (str): 队列名称
        """
        super().__init__(message, "CONSUMER_ERROR")
        self.queue_name = queue_name


class ConfigurationError(MQConsumerError):
    """配置相关异常"""
    
    def __init__(self, message: str, config_key: str = None):
        """
        初始化配置异常
        
        Args:
            message (str): 错误消息
            config_key (str): 配置项名称
        """
        super().__init__(message, "CONFIG_ERROR")
        self.config_key = config_key
