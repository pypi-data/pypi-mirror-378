#!/usr/bin/env python3
"""
统一文件上传服务

提供图片、视频等文件的上传功能，支持重试和错误恢复
"""

import os
import logging
import time
import mimetypes
from typing import Optional, Dict, Any, Union
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import urllib3

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class FileUploader:
    """
    统一文件上传器
    
    支持自动获取上传地址、重试机制、多种文件类型
    """
    
    def __init__(self, 
                 upload_host_api: str = '',
                 max_retries: int = 3,
                 timeout: int = 30,
                 verify_ssl: bool = False):
        """
        初始化上传器
        
        Args:
            upload_host_api: 获取上传地址的API
            max_retries: 最大重试次数
            timeout: 请求超时时间(秒)
            verify_ssl: 是否验证SSL证书
        """
        self.upload_host_api = upload_host_api
        self.max_retries = max_retries
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        
        # 配置日志
        self.logger = logging.getLogger(__name__)
        
        # 配置requests会话，支持重试
        self.session = requests.Session()
        try:
            # 尝试新版本的参数名
            retry_strategy = Retry(
                total=max_retries,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE", "OPTIONS", "TRACE"]
            )
        except TypeError:
            # 兼容旧版本的参数名
            retry_strategy = Retry(
                total=max_retries,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
                method_whitelist=["HEAD", "GET", "POST", "PUT", "DELETE", "OPTIONS", "TRACE"]
            )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
    def _log_info(self, msg: str):
        """记录信息日志（静默）"""
        self.logger.info(msg)
    
    def _log_error(self, msg: str):
        """记录错误日志"""
        self.logger.error(msg)
        print(f"❌ {msg}")
    
    def _log_success(self, msg: str):
        """记录成功日志"""
        self.logger.info(msg)
        print(f"✅ {msg}")
    
    def get_upload_host(self) -> Optional[str]:
        """
        获取上传服务器地址
        
        Returns:
            上传地址，失败返回None
        """
        try:
            response = self.session.get(
                self.upload_host_api, 
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            response.raise_for_status()
            
            data = response.json()
            upload_host = data.get('info', '')  # 直接从info字段获取上传地址
            
            if upload_host:
                return upload_host
            else:
                self._log_error("获取上传地址失败: 服务器返回空地址")
                return None
                
        except Exception as e:
            self._log_error(f"获取上传地址失败: {str(e)}")
            return None
    
    def validate_file(self, file_path: Union[str, Path]) -> bool:
        """
        验证文件基本信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件是否有效
        """
        file_path = Path(file_path)
        
        # 检查文件是否存在
        if not file_path.exists():
            self._log_error(f"文件不存在: {file_path}")
            return False
        
        # 检查是否是文件
        if not file_path.is_file():
            self._log_error(f"路径不是文件: {file_path}")
            return False
        
        # 检查文件大小
        file_size = file_path.stat().st_size
        if file_size == 0:
            self._log_error(f"文件为空: {file_path}")
            return False
        
        return True
    
    def get_file_info(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        获取文件信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件信息字典
        """
        file_path = Path(file_path)
        file_size = file_path.stat().st_size
        file_size_mb = file_size / (1024 * 1024)
        file_ext = file_path.suffix.lower()
        
        # 获取MIME类型
        mime_type, _ = mimetypes.guess_type(str(file_path))
        
        return {
            'name': file_path.name,
            'path': str(file_path),
            'size': file_size,
            'size_mb': round(file_size_mb, 2),
            'extension': file_ext,
            'mime_type': mime_type
        }
    
    def upload_file(self, 
                   file_path: Union[str, Path], 
                   upload_host: Optional[str] = None,
                   custom_filename: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        上传单个文件
        
        Args:
            file_path: 文件路径
            upload_host: 指定上传地址，为None时自动获取
            custom_filename: 自定义文件名
            
        Returns:
            上传结果，失败返回None
        """
        file_path = Path(file_path)
        
        # 验证文件
        if not self.validate_file(file_path):
            return None
        
        # 获取文件信息
        file_info = self.get_file_info(file_path)
        
        # 获取上传地址
        if not upload_host:
            upload_host = self.get_upload_host()
            if not upload_host:
                return None
        
        # 执行上传（带重试）
        for attempt in range(1, self.max_retries + 1):
            try:
                # 准备文件数据
                filename = custom_filename or file_path.name
                
                with open(file_path, 'rb') as f:
                    files = {
                        'file': (filename, f, file_info['mime_type'])
                    }
                    
                    # 执行上传
                    response = self.session.post(
                        upload_host,
                        files=files,
                        timeout=self.timeout,
                        verify=self.verify_ssl
                    )
                
                # 检查响应
                if response.status_code == 200:
                    try:
                        result = response.json()
                        
                        # 检查上传结果并显示相应信息
                        if result.get('code') == 1:  # 上传成功
                            file_url = result.get('info', '')
                            self._log_success(f"{file_url}")
                        else:  # 上传失败
                            error_msg = result.get('info', result.get('msg', '未知错误'))
                            self._log_error(f"{error_msg}")
                        
                        # 添加文件信息到结果中
                        result['file_info'] = file_info
                        result['upload_time'] = time.time()
                        
                        return result
                    except ValueError:
                        self._log_error(f"上传失败: 响应不是有效的JSON: {response.text}")
                        
                else:
                    self._log_error(f"上传失败: HTTP状态码 {response.status_code}")
                    if response.text:
                        self._log_error(f"错误详情: {response.text}")
            
            except Exception as e:
                if attempt < self.max_retries:
                    wait_time = 2 ** attempt  # 指数退避
                    time.sleep(wait_time)
                else:
                    self._log_error(f"上传失败: {str(e)}")
        
        return None
    
    def upload_image(self, file_path: Union[str, Path], **kwargs) -> Optional[Dict[str, Any]]:
        """
        上传图片文件（便捷方法，等同于upload_file）
        
        Args:
            file_path: 图片文件路径
            **kwargs: 传递给upload_file的其他参数
            
        Returns:
            上传结果
        """
        return self.upload_file(file_path, **kwargs)
    
    def upload_video(self, file_path: Union[str, Path], **kwargs) -> Optional[Dict[str, Any]]:
        """
        上传视频文件（便捷方法，等同于upload_file）
        
        Args:
            file_path: 视频文件路径
            **kwargs: 传递给upload_file的其他参数
            
        Returns:
            上传结果
        """
        return self.upload_file(file_path, **kwargs)
    
    def batch_upload(self, 
                    file_paths: list, 
                    upload_host: Optional[str] = None,
                    stop_on_error: bool = False) -> Dict[str, Any]:
        """
        批量上传文件
        
        Args:
            file_paths: 文件路径列表
            upload_host: 指定上传地址
            stop_on_error: 遇到错误是否停止
            
        Returns:
            批量上传结果统计
        """
        results = {
            'total': len(file_paths),
            'success': 0,
            'failed': 0,
            'results': [],
            'errors': []
        }
        
        self._log_info(f"开始批量上传 {len(file_paths)} 个文件")
        
        for i, file_path in enumerate(file_paths, 1):
            self._log_info(f"进度: {i}/{len(file_paths)} - {file_path}")
            
            result = self.upload_file(file_path, upload_host)
            
            if result:
                results['success'] += 1
                results['results'].append({
                    'file': str(file_path),
                    'status': 'success',
                    'result': result
                })
            else:
                results['failed'] += 1
                error_info = {
                    'file': str(file_path),
                    'status': 'failed',
                    'error': 'Upload failed'
                }
                results['results'].append(error_info)
                results['errors'].append(error_info)
                
                if stop_on_error:
                    self._log_error("遇到错误，停止批量上传")
                    break
        
        self._log_success(f"批量上传完成: 成功 {results['success']}, 失败 {results['failed']}")
        return results


# 便捷函数
def upload_image(file_path: Union[str, Path], **kwargs) -> Optional[Dict[str, Any]]:
    """
    便捷的图片上传函数
    
    Args:
        file_path: 图片文件路径
        **kwargs: 传递给FileUploader的参数
        
    Returns:
        上传结果
    """
    uploader = FileUploader(**kwargs)
    return uploader.upload_image(file_path)


def upload_video(file_path: Union[str, Path], **kwargs) -> Optional[Dict[str, Any]]:
    """
    便捷的视频上传函数
    
    Args:
        file_path: 视频文件路径
        **kwargs: 传递给FileUploader的参数
        
    Returns:
        上传结果
    """
    uploader = FileUploader(**kwargs)
    return uploader.upload_video(file_path)


def upload_file(file_path: Union[str, Path], **kwargs) -> Optional[Dict[str, Any]]:
    """
    便捷的文件上传函数
    
    Args:
        file_path: 文件路径
        **kwargs: 传递给FileUploader的参数
        
    Returns:
        上传结果
    """
    uploader = FileUploader(**kwargs)
    return uploader.upload_file(file_path)
