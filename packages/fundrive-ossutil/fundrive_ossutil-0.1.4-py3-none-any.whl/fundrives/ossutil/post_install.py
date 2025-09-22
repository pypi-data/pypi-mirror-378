"""
安装后执行脚本

在包安装完成后自动执行ossutil安装。
"""

import sys
from .install import install_ossutil, is_ossutil_installed


def post_install():
    """包安装后执行的函数"""
    print("fundrive-ossutil: 正在检查ossutil安装状态...")

    try:
        if not is_ossutil_installed():
            print("fundrive-ossutil: 开始自动安装ossutil命令行工具...")
            success = install_ossutil()
            if success:
                print("fundrive-ossutil: ossutil安装成功！")
                print("fundrive-ossutil: 您现在可以使用 fundrive-ossutil 包了")
            else:
                print("fundrive-ossutil: ossutil自动安装失败")
                print("fundrive-ossutil: 请稍后手动运行以下命令安装：")
                print(
                    "python -c 'from fundrives.ossutil import install_ossutil; install_ossutil()'"
                )
        else:
            print("fundrive-ossutil: ossutil已安装，无需重复安装")
    except Exception as e:
        print(f"fundrive-ossutil: 安装检查过程中出现异常: {e}")
        print("fundrive-ossutil: 请稍后手动安装ossutil")


if __name__ == "__main__":
    post_install()
