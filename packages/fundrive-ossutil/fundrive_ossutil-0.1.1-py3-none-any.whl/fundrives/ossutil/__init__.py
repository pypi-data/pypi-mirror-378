"""
fundrive-ossutil: 阿里云OSS命令行工具ossutil的Python包装器

提供更加友好的Python接口来使用阿里云OSS服务。
"""

from .install import (
    OSSUtilInstaller,
    install_ossutil,
    get_ossutil_path,
    is_ossutil_installed,
)

__version__ = "0.1.0"
__author__ = "farfarfun"
__email__ = "farfarfun@gmail.com"

__all__ = [
    "OSSUtilInstaller",
    # 便捷函数
    "install_ossutil",
    "get_ossutil_path",
    "is_ossutil_installed",
]
