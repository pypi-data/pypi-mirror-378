"""
fundrive-ossutil: 阿里云OSS命令行工具ossutil的Python包装器

提供更加友好的Python接口来使用阿里云OSS服务。

使用说明：
1. 安装包后，首次使用时会自动检测并安装ossutil
2. 如需手动安装：install-ossutil 或 from fundrives.ossutil import install_ossutil; install_ossutil()
3. 如需禁用自动安装：设置环境变量 FUNDRIVE_OSSUTIL_NO_AUTO_INSTALL=1
"""

import os
import atexit
from pathlib import Path
from .install import install_ossutil, get_ossutil_path, is_ossutil_installed

__version__ = "0.1.3"
__author__ = "farfarfun"
__email__ = "farfarfun@gmail.com"

# 安装状态缓存
_install_checked = False
_ossutil_available = False


def _get_install_marker_file():
    """获取安装标记文件路径"""
    home_dir = Path.home()
    return home_dir / ".fundrive" / "ossutil_install_marker"


def _check_and_install_ossutil():
    """检查并安装ossutil（如果需要）"""
    global _install_checked, _ossutil_available

    if _install_checked:
        return _ossutil_available

    _install_checked = True

    # 检查是否已经安装
    if is_ossutil_installed():
        _ossutil_available = True
        return True

    # 检查环境变量是否禁用自动安装
    if os.environ.get("FUNDRIVE_OSSUTIL_NO_AUTO_INSTALL", "").lower() in (
        "1",
        "true",
        "yes",
    ):
        _ossutil_available = False
        return False

    # 检查是否已经尝试过安装
    marker_file = _get_install_marker_file()
    if marker_file.exists():
        marker_content = marker_file.read_text().strip()
        if marker_content == "installed_successfully":
            # 重新检查是否真的安装成功了
            _ossutil_available = is_ossutil_installed()
            return _ossutil_available
        elif marker_content == "install_failed":
            _ossutil_available = False
            return False

    # 尝试自动安装
    try:
        from funutil import getLogger

        logger = getLogger("fundrive-ossutil")

        print("🔧 fundrive-ossutil: 检测到ossutil未安装，正在自动安装...")
        print("💡 如需禁用自动安装，请设置环境变量: FUNDRIVE_OSSUTIL_NO_AUTO_INSTALL=1")

        success = install_ossutil()

        # 创建标记文件
        marker_file.parent.mkdir(parents=True, exist_ok=True)

        if success:
            marker_file.write_text("installed_successfully")
            _ossutil_available = True
            print("✅ fundrive-ossutil: ossutil安装成功！")
        else:
            marker_file.write_text("install_failed")
            _ossutil_available = False
            print("⚠️  fundrive-ossutil: ossutil自动安装失败")
            print("🔧 请手动运行: install-ossutil")

    except Exception as e:
        print(f"❌ fundrive-ossutil: 自动安装ossutil时发生错误: {e}")
        print("🔧 请手动运行: install-ossutil")
        _ossutil_available = False

        # 记录失败状态
        try:
            marker_file.parent.mkdir(parents=True, exist_ok=True)
            marker_file.write_text("install_failed")
        except:
            pass

    return _ossutil_available


def ensure_ossutil_installed():
    """确保ossutil已安装，如果未安装则尝试安装"""
    return _check_and_install_ossutil()


# 延迟导入OSSUtil类，确保在使用时才检查ossutil
def __getattr__(name):
    """延迟加载模块属性"""
    if name == "OSSUtil":
        # 在首次使用OSSUtil时检查并安装ossutil
        ensure_ossutil_installed()
        from .ossutil import OSSUtil

        return OSSUtil
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = [
    "install_ossutil",
    "get_ossutil_path",
    "is_ossutil_installed",
    "ensure_ossutil_installed",
    "OSSUtil",
]
