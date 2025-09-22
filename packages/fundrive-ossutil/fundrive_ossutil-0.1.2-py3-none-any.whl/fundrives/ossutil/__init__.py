"""
fundrive-ossutil: 阿里云OSS命令行工具ossutil的Python包装器

提供更加友好的Python接口来使用阿里云OSS服务。
"""

import os
from .install import install_ossutil, get_ossutil_path, is_ossutil_installed

__version__ = "0.1.1"
__author__ = "farfarfun"
__email__ = "farfarfun@gmail.com"

__all__ = ["install_ossutil", "get_ossutil_path", "is_ossutil_installed"]


# 自动安装ossutil（仅在首次导入时执行）
def _auto_install_ossutil():
    """自动安装ossutil的内部函数"""
    # 检查环境变量，允许用户禁用自动安装
    if os.environ.get("FUNDRIVE_OSSUTIL_NO_AUTO_INSTALL", "").lower() in (
        "1",
        "true",
        "yes",
    ):
        return

    try:
        # 检查是否已安装
        if not is_ossutil_installed():
            print("fundrive-ossutil: 正在自动安装ossutil命令行工具...")
            success = install_ossutil()
            if success:
                print("fundrive-ossutil: ossutil安装成功！")
            else:
                print("fundrive-ossutil: ossutil自动安装失败，请手动安装或稍后重试")
    except Exception as e:
        print(f"fundrive-ossutil: 自动安装过程中出现异常: {e}")


# 执行自动安装
_auto_install_ossutil()
