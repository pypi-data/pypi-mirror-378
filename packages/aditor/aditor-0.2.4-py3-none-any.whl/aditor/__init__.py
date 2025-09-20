"""
Aditor - API客户端包

提供API登录认证和调用功能的Python包。
包含基础工具函数和API客户端类。
"""

__version__ = "0.2.4"
__author__ = "aditor"
__email__ = ""

from .core import Client

__all__ = [
    "Client"
]
