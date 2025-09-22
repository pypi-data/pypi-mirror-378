"""amap_mcp_server package"""

import argparse
from .server import mcp, main as server_main

__version__ = "0.1.26"
__author__ = "lengyue1084"
__email__ = "95695864@qq.com"

# 从server模块导入工具函数
from .server import lucky_star, num_add, greeting

# 简化main函数，避免重复定义
def main():
    """Entry point for the MCP server"""
    server_main()

if __name__ == "__main__":
    main()