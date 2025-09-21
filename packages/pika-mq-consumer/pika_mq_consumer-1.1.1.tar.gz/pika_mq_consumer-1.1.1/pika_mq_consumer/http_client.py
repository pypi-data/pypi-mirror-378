#!/usr/bin/env python3
"""
简化的HTTP POST客户端

只提供POST请求功能，使用application/x-www-form-urlencoded格式
"""

import time
import logging
from typing import Optional, Dict, Any

import requests
import urllib3

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def http_post(url: str, 
              data: Optional[Dict[str, Any]] = None,
              retries: int = 3) -> Optional[Dict[str, Any]]:
    """
    发送POST请求，使用application/x-www-form-urlencoded格式
    
    Args:
        url: 请求URL
        data: 表单数据字典
        retries: 重试次数，默认3次
        
    Returns:
        JSON响应字典或None
    """
    
    def _log_error(msg: str):
        """记录错误日志"""
        print(f"❌ {msg}")
    
    # 设置请求头
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'pika-mq-consumer/1.1.0'
    }
    
    for attempt in range(1, retries + 1):
        try:
            response = requests.post(
                url=url,
                data=data,
                headers=headers,
                timeout=30,
                verify=False  # 不验证SSL
            )
            
            # 检查响应状态
            if response.status_code == 200:
                try:
                    result = response.json()
                    return result
                except ValueError:
                    # 不是JSON响应，返回文本
                    return {"success": True, "text": response.text, "status_code": response.status_code}
            else:
                if attempt == retries:
                    _log_error(f"HTTP {response.status_code}: {response.text}")
                    return {"success": False, "error": f"HTTP {response.status_code}", "text": response.text}
                    
        except requests.exceptions.RequestException as e:
            if attempt == retries:
                _log_error(f"请求失败: {str(e)}")
                return {"success": False, "error": str(e)}
            else:
                # 指数退避重试
                wait_time = 2 ** attempt
                time.sleep(wait_time)
        
        except Exception as e:
            if attempt == retries:
                _log_error(f"请求异常: {str(e)}")
                return {"success": False, "error": str(e)}
            else:
                wait_time = 2 ** attempt
                time.sleep(wait_time)
    
    return None
