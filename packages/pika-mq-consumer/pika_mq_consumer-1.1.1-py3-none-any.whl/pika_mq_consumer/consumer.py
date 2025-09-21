"""
MQ消费者核心模块

完全参考amqplib-init实现，提供与Node.js版本一致的API和功能。
支持：自动重连、自动重载、并发控制、延迟ACK、自动获取连接信息等。
"""

import json
import logging
import threading
import time
import asyncio
import subprocess
import os
import signal
from typing import Callable, Dict, Any, Optional, Union, Awaitable
from functools import wraps
import requests

import pika
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties

from .exceptions import MQConsumerError, ConnectionError, ConsumerError, ConfigurationError


class MQConsumer:
    """
    RabbitMQ消费者 - 完全参考amqplib-init实现
    
    提供与Node.js版本完全一致的API和功能特性：
    - 自动获取连接信息 (amqp_auto_link)
    - 自动重连机制
    - 自动重载 (基于队列状态)
    - 并发控制 (prefetch)
    - 延迟ACK
    - 钩子函数支持
    """
    
    @staticmethod
    async def init(option: Dict[str, Any]) -> None:
        """
        初始化MQ消费者 - 完全参考amqplib-init的init函数
        
        Args:
            option (dict): 配置选项，与Node.js版本保持一致
                - channel_name (str): 频道名称，默认'node-test-channel'
                - prefetch (int): 预取计数，默认1
                - pm_id (str): PM2进程ID，默认'0'
                - callback (callable): 消息处理回调
                - finish (callable): 初始化完成回调
                - amqp_link (str): RabbitMQ连接地址
                - amqp_auto_link (str): 自动获取连接信息的HTTPS链接
                - heartbeat (int): 心跳间隔，默认5秒
                - timeout (int): 连接超时时间，默认2000毫秒
                - delay (int): 延迟ACK时间，默认0毫秒
                - auto_reload (int): 自动重载间隔，默认0毫秒（不自动重载）
                - query_hook (callable): 查询钩子，用于判断是否有其他消息来源
                - init_hook (callable): 初始化钩子，连接成功后执行
                - log_level (str): 日志级别，默认'quiet'
                  可选值: 'quiet'(精简), 'normal'(正常), 'verbose'(详细), 'debug'(调试)
                - show_message_content (bool): 是否显示消息内容，默认False
        """
        # 解析配置参数，与Node.js版本保持一致
        channel_name = option.get('channel_name', 'node-test-channel')
        prefetch = option.get('prefetch', 1)
        pm_id = option.get('pm_id', '0')
        callback = option.get('callback', lambda x: None)
        finish = option.get('finish', lambda: None)
        amqp_link = option.get('amqp_link', '')
        amqp_auto_link = option.get('amqp_auto_link', '')
        heartbeat = option.get('heartbeat', 5)
        timeout = option.get('timeout', 2000)
        delay = option.get('delay', 0)
        auto_reload = option.get('auto_reload', 0)
        query_hook = option.get('query_hook', lambda: True)
        init_hook = option.get('init_hook', lambda x: None)
        log_level = option.get('log_level', 'quiet')  # 默认精简模式
        show_message_content = option.get('show_message_content', False)  # 默认不显示消息内容
        
        durable = True  # 队列持久化，默认为True
        connection = None
        channel = None
        
        # 配置日志级别和pika库日志
        log_level_map = {
            'quiet': logging.ERROR,      # 精简：只显示错误
            'normal': logging.WARNING,   # 正常：显示警告和错误
            'verbose': logging.INFO,     # 详细：显示信息、警告、错误
            'debug': logging.DEBUG       # 调试：显示所有日志
        }
        
        # 注意：不再强制重设根日志级别，保持与主程序日志配置一致
        # 只设置pika库的日志级别，避免干扰主程序的日志系统
        current_log_level = log_level_map.get(log_level, logging.ERROR)
        
        # 仅控制pika库日志级别，不影响其他日志器
        pika_log_level = logging.ERROR if log_level == 'quiet' else current_log_level
        logging.getLogger('pika').setLevel(pika_log_level)
        logging.getLogger('pika.adapters').setLevel(pika_log_level)
        logging.getLogger('pika.connection').setLevel(pika_log_level)
        
        # 配置日志记录器
        logger = logging.getLogger(__name__)
        
        def log_info(msg: str):
            """信息日志 - 根据级别控制输出"""
            if log_level in ['verbose', 'debug']:
                logger.info(f"ℹ️  {msg}")
        
        def log_error(msg: str):
            """错误日志 - 始终显示"""
            logger.error(f"❌ {msg}")
        
        def log_success(msg: str):
            """成功日志 - 根据级别控制输出"""
            if log_level in ['quiet', 'normal', 'verbose', 'debug']:  # quiet模式也显示成功信息
                logger.info(f"✅ {msg}")
        
        def log_config(msg: str):
            """配置日志 - quiet模式也显示"""
            if log_level in ['quiet', 'normal', 'verbose', 'debug']:
                logger.info(f"🔧 {msg}")
        
        def log_status(msg: str):
            """状态日志 - quiet模式也显示重要状态"""
            if log_level in ['quiet', 'normal', 'verbose', 'debug']:
                logger.info(f"📊 {msg}")
        
        def log_debug(msg: str):
            """调试日志 - 仅debug模式显示"""
            if log_level == 'debug':
                logger.debug(f"🔍 {msg}")
        
        def log_message(content: Any):
            """消息内容日志 - 根据show_message_content控制"""
            if show_message_content and log_level in ['verbose', 'debug']:
                logger.info(f"📄 消息内容: {json.dumps(content, ensure_ascii=False, indent=2)}")
            elif log_level == 'quiet' and not show_message_content:
                # quiet模式下简单显示收到消息
                logger.info(f"📨 收到消息 (内容已隐藏)")
            
        # 显示基本配置信息
        log_config("MQ消费者配置:")
        log_config(f"  队列名称: {channel_name}")
        log_config(f"  并发设置: {prefetch}")
        log_config(f"  日志级别: {log_level}")
        log_config(f"  延迟ACK: {delay}ms")
        if show_message_content:
            log_config(f"  消息内容: 显示")
        else:
            log_config(f"  消息内容: 隐藏")
        
        # 处理 amqp_auto_link 自动获取连接信息
        final_amqp_link = amqp_link
        if amqp_auto_link:
            try:
                log_config(f"正在自动获取连接配置...")
                response = requests.post(amqp_auto_link)
                data = response.json()
                info = data.get('info', {})
                
                if all(key in info for key in ['AMQPLIB_USER', 'AMQPLIB_PWD', 'AMQPLIB_PUB', 'AMQPLIB_PORT']):
                    final_amqp_link = f"amqp://{info['AMQPLIB_USER']}:{info['AMQPLIB_PWD']}@{info['AMQPLIB_PUB']}:{info['AMQPLIB_PORT']}"
                    log_success(f"连接配置获取成功: {info['AMQPLIB_PUB']}:{info['AMQPLIB_PORT']}")
                else:
                    log_error("获取的连接信息不完整，使用默认连接地址")
            except Exception as e:
                log_error(f"获取连接信息失败: {str(e)}")
                log_config("使用默认连接地址继续...")
        
        async def sleep_async(seconds: float):
            """异步睡眠"""
            await asyncio.sleep(seconds)
        
        def sleep_sync(seconds: float):
            """同步睡眠"""
            time.sleep(seconds)
        
        async def reconnect():
            """重连函数 - 完全参考Node.js版本"""
            nonlocal connection, channel
            log_error("连接丢失，正在尝试重连...")
            await sleep_async(2)  # 重连前等待2秒
            
            try:
                # 解析连接URL
                connection_params = pika.URLParameters(final_amqp_link)
                connection_params.heartbeat = heartbeat
                connection_params.connection_attempts = 3
                connection_params.retry_delay = 2
                
                connection = pika.BlockingConnection(connection_params)
                channel = connection.channel()
                channel.queue_declare(queue=channel_name, durable=durable)
                channel.basic_qos(prefetch_count=prefetch)
                
                # 执行初始化钩子
                if asyncio.iscoroutinefunction(init_hook):
                    await init_hook({'channel': channel, 'connection': connection})
                else:
                    init_hook({'channel': channel, 'connection': connection})
                
                log_success(f"已重新连接到RabbitMQ")
                log_status(f"恢复监听队列: {channel_name}")
                await consume_messages()  # 开始消费消息
                
            except Exception as e:
                log_error(f"重连失败: {str(e)}")
                # 继续尝试重连
                await asyncio.sleep(5)
                await reconnect()
        
        async def consume_messages():
            """消费消息函数 - 完全参考Node.js版本"""
            log_debug(f"开始消费: {channel_name}")
            
            def message_callback(ch, method, properties, body):
                """消息回调处理"""
                if body is not None:
                    try:
                        # 解析消息内容
                        content = json.loads(body.decode('utf-8'))
                        log_debug(f"🪴 队列收到消息")
                        log_message(content)  # 根据配置决定是否显示消息内容
                        start_time = time.time() * 1000  # 毫秒时间戳
                        
                        # 创建处理Promise
                        def handle_message():
                            try:
                                # 执行消息处理回调
                                if asyncio.iscoroutinefunction(callback):
                                    # 异步回调 - 保持与主程序相同的事件循环和日志配置
                                    try:
                                        # 尝试获取现有的事件循环
                                        loop = asyncio.get_event_loop()
                                    except RuntimeError:
                                        # 如果没有事件循环，创建新的
                                        loop = asyncio.new_event_loop()
                                        asyncio.set_event_loop(loop)
                                    
                                    # 在事件循环中运行回调
                                    if loop.is_running():
                                        # 如果循环正在运行，创建任务
                                        import concurrent.futures
                                        with concurrent.futures.ThreadPoolExecutor() as executor:
                                            future = executor.submit(
                                                lambda: asyncio.run(callback(content))
                                            )
                                            result = future.result()
                                    else:
                                        # 如果循环未运行，直接运行
                                        result = loop.run_until_complete(callback(content))
                                else:
                                    # 同步回调
                                    result = callback(content)
                                
                                # 处理成功
                                end_time = time.time() * 1000 - start_time
                                log_debug(f"☘️ 消息处理完成，延迟: {delay}ms，总时间: {end_time:.0f}ms")
                                
                                # 延迟ACK
                                def delayed_ack():
                                    try:
                                        ch.basic_ack(delivery_tag=method.delivery_tag)
                                    except Exception as e:
                                        log_error(f"ACK失败: {str(e)}")
                                
                                if delay > 0:
                                    threading.Timer(delay / 1000.0, delayed_ack).start()
                                else:
                                    delayed_ack()
                                    
                            except Exception as e:
                                # 处理失败
                                log_error(f"‼️ 处理消息返回错误: {str(e)}")
                                sleep_sync(5)
                                try:
                                    ch.basic_reject(delivery_tag=method.delivery_tag, requeue=True)
                                except Exception as reject_error:
                                    log_error(f"拒绝消息失败: {str(reject_error)}")
                        
                        # 在新线程中处理消息
                        threading.Thread(target=handle_message, daemon=True).start()
                        
                    except json.JSONDecodeError as e:
                        log_error(f"‼️ 处理消息时出错: JSON解析失败 - {str(e)}")
                        sleep_sync(5)
                        try:
                            ch.basic_reject(delivery_tag=method.delivery_tag, requeue=True)
                        except Exception as reject_error:
                            log_error(f"拒绝消息失败: {str(reject_error)}")
                    except Exception as e:
                        log_error(f"‼️ 处理消息时出错: {str(e)}")
                        sleep_sync(5)
                        try:
                            ch.basic_reject(delivery_tag=method.delivery_tag, requeue=True)
                        except Exception as reject_error:
                            log_error(f"拒绝消息失败: {str(reject_error)}")
                else:
                    # 处理空消息
                    try:
                        ch.basic_ack(delivery_tag=method.delivery_tag)
                        log_error(f"收到无效消息(自动消费): {body}")
                    except Exception as e:
                        log_error(f"处理无效消息失败: {str(e)}")
            
            # 开始消费
            try:
                channel.basic_consume(
                    queue=channel_name,
                    on_message_callback=message_callback,
                    auto_ack=False  # 手动ACK
                )
                
                # 在新线程中启动消费循环
                def start_consuming():
                    try:
                        channel.start_consuming()
                    except Exception as e:
                        log_error(f"消费过程中出错: {str(e)}")
                        # 触发重连
                        asyncio.run(reconnect())
                
                consuming_thread = threading.Thread(target=start_consuming, daemon=True)
                consuming_thread.start()
                
            except Exception as e:
                log_error(f"启动消费失败: {str(e)}")
                raise ConsumerError(f"启动消费失败: {str(e)}")
        
        async def start():
            """启动函数 - 完全参考Node.js版本"""
            nonlocal connection, channel
            
            try:
                # 创建连接
                connection_params = pika.URLParameters(final_amqp_link)
                connection_params.heartbeat = heartbeat
                connection_params.connection_attempts = 3
                connection_params.retry_delay = 2
                
                connection = pika.BlockingConnection(connection_params)
                channel = connection.channel()
                channel.queue_declare(queue=channel_name, durable=durable)
                channel.basic_qos(prefetch_count=prefetch)
                
                # 执行初始化钩子
                if asyncio.iscoroutinefunction(init_hook):
                    await init_hook({'channel': channel, 'connection': connection})
                else:
                    init_hook({'channel': channel, 'connection': connection})
                
                log_success(f"已连接到RabbitMQ")
                log_status(f"开始监听队列: {channel_name}")
                await consume_messages()  # 开始消费消息
                
                # 连接错误处理
                def on_connection_error():
                    log_error("检测到连接错误")
                    asyncio.run(reconnect())
                
                def on_connection_close():
                    log_error("与RabbitMQ的连接已关闭")
                    asyncio.run(reconnect())
                
                # 监控连接状态（简化版）
                def monitor_connection():
                    while True:
                        try:
                            if connection.is_closed:
                                on_connection_close()
                                break
                            time.sleep(1)
                        except Exception:
                            on_connection_error()
                            break
                
                monitor_thread = threading.Thread(target=monitor_connection, daemon=True)
                monitor_thread.start()
                
                # 自动重载逻辑
                if auto_reload > 0:
                    async def auto_reload_task():
                        while True:
                            try:
                                await sleep_async(auto_reload / 1000.0)
                                
                                # 检查队列长度
                                method = channel.queue_declare(queue=channel_name, passive=True)
                                message_count = method.method.message_count
                                
                                # 执行查询钩子
                                if asyncio.iscoroutinefunction(query_hook):
                                    hook_result = await query_hook()
                                else:
                                    hook_result = query_hook()
                                
                                log_info(f"MQ队列中有 {message_count} 条消息，检测是否可以重启: {1 if hook_result else 0}")
                                
                                if message_count == 0 and hook_result:
                                    log_info("队列中没有消息，正在重载服务...")
                                    # 使用PM2或systemctl重载服务
                                    try:
                                        subprocess.run(['pm2', 'reload', str(pm_id)], check=True)
                                    except subprocess.CalledProcessError:
                                        # 如果PM2不可用，尝试其他重启方式
                                        try:
                                            # 发送SIGUSR1信号给当前进程（可以自定义处理）
                                            os.kill(os.getpid(), signal.SIGUSR1)
                                        except Exception as e:
                                            log_error(f"重载服务失败: {str(e)}")
                                            
                            except Exception as e:
                                log_error(f"检查队列长度时出错: {str(e)}")
                    
                    # 启动自动重载任务
                    reload_thread = threading.Thread(
                        target=lambda: asyncio.run(auto_reload_task()), 
                        daemon=True
                    )
                    reload_thread.start()
                
                # 执行初始化完成回调
                if asyncio.iscoroutinefunction(finish):
                    await finish()
                else:
                    finish()
                    
            except Exception as e:
                log_error(f"初始化RabbitMQ连接时出错: {str(e)}")
                raise ConnectionError(f"初始化RabbitMQ连接时出错: {str(e)}")
        
        # 返回启动函数并立即执行
        await start()


# 兼容旧版本API的包装类
class MQConsumerLegacy:
    """
    兼容旧版本API的消费者类
    
    保持向后兼容性，同时提供新的init方法
    """
    
    def __init__(self, **kwargs):
        """传统初始化方式，保持兼容性"""
        self.config = kwargs
        self.logger = logging.getLogger(__name__)
    
    async def init(self, option: Dict[str, Any]) -> None:
        """
        新的init方法，与Node.js版本完全一致
        
        使用方式：
        consumer = MQConsumerLegacy()
        await consumer.init({
            'channel_name': 'my-queue',
            'callback': my_callback_function,
            'amqp_auto_link': 'https://api.example.com/config',
            # ... 其他配置
        })
        """
        await MQConsumer.init(option)
    
    def queue(self, queue_name: str, **options):
        """装饰器方式（兼容旧版本）"""
        def decorator(handler_func):
            # 这里可以实现装饰器逻辑
            @wraps(handler_func)
            def wrapper(*args, **kwargs):
                return handler_func(*args, **kwargs)
            return wrapper
        return decorator