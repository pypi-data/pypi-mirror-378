"""
koxs-color - 强大的终端颜色输出库

提供两种使用方式：
1. 直接打印: from koxs_color import koxs
2. 返回字符串: from koxs_color import koxy

版本: 0.1.0
作者: 您的名字
"""

# 导入所有功能，方便用户使用
from .koxs import *
from .koxy import *

__version__ = "0.1.0"
__author__ = "您的名字"

def demo():
    """显示所有颜色的演示"""
    from . import koxs, koxy
    
    print("\n=== koxs-color 演示 ===\n")
    
    # 使用 koxs (直接打印)
    koxs.koxs_print_red("红色文字 - 直接打印")
    koxs.koxs_print_green("绿色文字 - 直接打印")
    koxs.koxs_print_blue("蓝色文字 - 直接打印")
    
    print()
    
    # 使用 koxy (返回字符串)
    print(koxy.koxs_red("红色文字 - 返回字符串"))
    print(koxy.koxs_green("绿色文字 - 返回字符串")) 
    print(koxy.koxs_blue("蓝色文字 - 返回字符串"))
    
    print("\n=== 演示结束 ===\n")