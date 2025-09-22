"""
ossutil自动安装模块

提供ossutil命令行工具的自动下载和安装功能。
支持多平台（Windows、macOS、Linux）的自动检测和安装。
"""

import os
import platform
import subprocess
import tempfile
import urllib.request
from pathlib import Path
from typing import Optional

from funutil import getLogger


logger = getLogger("fundrive-ossutil")


class OSSUtilInstaller:
    """ossutil安装器

    负责检测系统环境并自动下载安装ossutil命令行工具。
    """

    # ossutil下载URL模板
    DOWNLOAD_URLS = {
        "windows": {
            "x86_64": "https://gosspublic.alicdn.com/ossutil/1.7.19/ossutil-v1.7.19-windows-amd64.zip",
            "x86": "https://gosspublic.alicdn.com/ossutil/1.7.19/ossutil-v1.7.19-windows-386.zip",
        },
        "darwin": {
            "x86_64": "https://gosspublic.alicdn.com/ossutil/1.7.19/ossutil-v1.7.19-darwin-amd64.zip",
            "arm64": "https://gosspublic.alicdn.com/ossutil/1.7.19/ossutil-v1.7.19-darwin-arm64.zip",
        },
        "linux": {
            "x86_64": "https://gosspublic.alicdn.com/ossutil/1.7.19/ossutil-v1.7.19-linux-amd64.zip",
            "x86": "https://gosspublic.alicdn.com/ossutil/1.7.19/ossutil-v1.7.19-linux-386.zip",
            "arm64": "https://gosspublic.alicdn.com/ossutil/1.7.19/ossutil-v1.7.19-linux-arm64.zip",
        },
    }

    def __init__(self):
        """初始化安装器"""
        self.system = platform.system().lower()
        self.machine = platform.machine().lower()
        self.install_dir = self._get_install_directory()

    def _get_install_directory(self) -> Path:
        """获取安装目录

        Returns:
            安装目录路径
        """
        if self.system == "windows":
            # Windows: 使用用户目录下的.ossutil文件夹
            install_dir = Path.home() / ".ossutil"
        else:
            # Unix-like: 使用/usr/local/bin或用户目录
            if os.access("/usr/local/bin", os.W_OK):
                install_dir = Path("/usr/local/bin")
            else:
                install_dir = Path.home() / ".local" / "bin"

        install_dir.mkdir(parents=True, exist_ok=True)
        return install_dir

    def _normalize_architecture(self) -> str:
        """标准化架构名称

        Returns:
            标准化的架构名称
        """
        arch_map = {
            "amd64": "x86_64",
            "x64": "x86_64",
            "i386": "x86",
            "i686": "x86",
            "aarch64": "arm64",
        }
        return arch_map.get(self.machine, self.machine)

    def _get_download_url(self) -> Optional[str]:
        """获取下载URL

        Returns:
            下载URL，如果不支持当前平台则返回None
        """
        arch = self._normalize_architecture()

        if self.system not in self.DOWNLOAD_URLS:
            logger.error(f"不支持的操作系统: {self.system}")
            return None

        system_urls = self.DOWNLOAD_URLS[self.system]
        if arch not in system_urls:
            logger.error(f"不支持的架构: {arch} (系统: {self.system})")
            return None

        return system_urls[arch]

    def _get_executable_name(self) -> str:
        """获取可执行文件名

        Returns:
            可执行文件名
        """
        return "ossutil.exe" if self.system == "windows" else "ossutil"

    def is_installed(self) -> bool:
        """检查ossutil是否已安装

        Returns:
            如果已安装返回True，否则返回False
        """
        try:
            # 首先检查系统PATH中是否有ossutil
            result = subprocess.run(
                ["ossutil", "version"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                logger.info("系统中已安装ossutil")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        # 检查本地安装目录
        executable_name = self._get_executable_name()
        local_path = self.install_dir / executable_name

        if local_path.exists() and local_path.is_file():
            try:
                result = subprocess.run(
                    [str(local_path), "version"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode == 0:
                    logger.info(f"本地已安装ossutil: {local_path}")
                    return True
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass

        return False

    def _download_file(self, url: str, dest_path: Path) -> bool:
        """下载文件

        Args:
            url: 下载URL
            dest_path: 目标文件路径

        Returns:
            下载成功返回True，失败返回False
        """
        try:
            logger.info(f"开始下载ossutil: {url}")

            with urllib.request.urlopen(url) as response:
                total_size = int(response.headers.get("content-length", 0))
                downloaded = 0

                with open(dest_path, "wb") as f:
                    while True:
                        chunk = response.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)

                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            logger.info(f"下载进度: {progress:.1f}%")

            logger.success(f"下载完成: {dest_path}")
            return True

        except Exception as e:
            logger.error(f"下载失败: {e}")
            return False

    def _extract_zip(self, zip_path: Path, extract_dir: Path) -> bool:
        """解压ZIP文件

        Args:
            zip_path: ZIP文件路径
            extract_dir: 解压目录

        Returns:
            解压成功返回True，失败返回False
        """
        try:
            import zipfile

            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_dir)

            logger.success(f"解压完成: {extract_dir}")
            return True

        except Exception as e:
            logger.error(f"解压失败: {e}")
            return False

    def _make_executable(self, file_path: Path) -> bool:
        """设置文件为可执行

        Args:
            file_path: 文件路径

        Returns:
            设置成功返回True，失败返回False
        """
        try:
            if self.system != "windows":
                os.chmod(file_path, 0o755)
            logger.info(f"设置可执行权限: {file_path}")
            return True
        except Exception as e:
            logger.error(f"设置可执行权限失败: {e}")
            return False

    def install(self) -> bool:
        """安装ossutil

        Returns:
            安装成功返回True，失败返回False
        """
        if self.is_installed():
            logger.info("ossutil已安装，跳过安装")
            return True

        download_url = self._get_download_url()
        if not download_url:
            return False

        logger.info(f"开始安装ossutil到: {self.install_dir}")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            zip_file = temp_path / "ossutil.zip"

            # 下载文件
            if not self._download_file(download_url, zip_file):
                return False

            # 解压文件
            extract_dir = temp_path / "extracted"
            if not self._extract_zip(zip_file, extract_dir):
                return False

            # 查找ossutil可执行文件
            executable_name = self._get_executable_name()

            # 在解压目录中查找ossutil可执行文件
            ossutil_path = None
            for root, dirs, files in os.walk(extract_dir):
                for file in files:
                    if file == executable_name or file.startswith("ossutil"):
                        candidate_path = Path(root) / file
                        if candidate_path.is_file():
                            ossutil_path = candidate_path
                            break
                if ossutil_path:
                    break

            if not ossutil_path:
                logger.error("在下载的文件中未找到ossutil可执行文件")
                return False

            # 复制到安装目录
            dest_path = self.install_dir / executable_name
            try:
                import shutil

                shutil.copy2(ossutil_path, dest_path)
                logger.success(f"复制ossutil到: {dest_path}")
            except Exception as e:
                logger.error(f"复制文件失败: {e}")
                return False

            # 设置可执行权限
            if not self._make_executable(dest_path):
                return False

            # 验证安装
            try:
                result = subprocess.run(
                    [str(dest_path), "version"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode == 0:
                    logger.success("ossutil安装成功！")
                    logger.info(f"版本信息: {result.stdout.strip()}")
                    return True
                else:
                    logger.error("ossutil安装验证失败")
                    return False
            except Exception as e:
                logger.error(f"ossutil安装验证失败: {e}")
                return False

    def get_executable_path(self) -> Optional[Path]:
        """获取ossutil可执行文件路径

        Returns:
            可执行文件路径，如果未找到返回None
        """
        # 首先尝试系统PATH
        try:
            result = subprocess.run(
                ["which", "ossutil"]
                if self.system != "windows"
                else ["where", "ossutil"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return Path(result.stdout.strip().split("\n")[0])
        except Exception as e:
            logger.error(f"error:{e}")

        # 检查本地安装目录
        executable_name = self._get_executable_name()
        local_path = self.install_dir / executable_name

        if local_path.exists() and local_path.is_file():
            return local_path

        return None


def install_ossutil() -> bool:
    """安装ossutil命令行工具

    这是一个便捷函数，用于自动检测系统环境并安装ossutil。

    Returns:
        安装成功返回True，失败返回False

    Example:
        >>> from fundrives.ossutil import install_ossutil
        >>> success = install_ossutil()
        >>> if success:
        ...     print("ossutil安装成功")
    """
    installer = OSSUtilInstaller()
    return installer.install()


def get_ossutil_path() -> Optional[str]:
    """获取ossutil可执行文件路径

    Returns:
        ossutil可执行文件路径，如果未找到返回None

    Example:
        >>> from fundrives.ossutil import get_ossutil_path
        >>> path = get_ossutil_path()
        >>> if path:
        ...     print(f"ossutil路径: {path}")
    """
    installer = OSSUtilInstaller()
    path = installer.get_executable_path()
    return str(path) if path else None


def is_ossutil_installed() -> bool:
    """检查ossutil是否已安装

    Returns:
        如果已安装返回True，否则返回False

    Example:
        >>> from fundrives.ossutil import is_ossutil_installed
        >>> if is_ossutil_installed():
        ...     print("ossutil已安装")
        ... else:
        ...     print("ossutil未安装")
    """
    installer = OSSUtilInstaller()
    return installer.is_installed()
