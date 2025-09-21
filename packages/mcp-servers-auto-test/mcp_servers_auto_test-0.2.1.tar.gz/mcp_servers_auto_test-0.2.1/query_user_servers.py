#!/usr/bin/env python3
"""
查询用户创建的MCP服务器实例
基于参考文件 /Users/xiexinfa/mcpmarket-quart/query_user_servers.py
"""

import asyncio
import sys
from src.user_server_manager import UserServerManager


async def query_user_servers(user_id: str, include_inactive: bool = False):
    """查询指定用户的所有MCP服务器实例"""
    manager = UserServerManager()
    await manager.print_user_servers_report(user_id, include_inactive)


def main():
    if len(sys.argv) < 2:
        print("用法: python query_user_servers.py <user_id> [--include-inactive]")
        print("示例: python query_user_servers.py 0992c0114e12600e43ef6fee2a1cd508")
        print("示例: python query_user_servers.py 0992c0114e12600e43ef6fee2a1cd508 --include-inactive")
        sys.exit(1)
    
    user_id = sys.argv[1]
    include_inactive = "--include-inactive" in sys.argv
    
    asyncio.run(query_user_servers(user_id, include_inactive))


if __name__ == "__main__":
    main()
