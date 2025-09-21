#!/usr/bin/env python3
"""
获取用户所有活跃MCP实例的URL
基于参考文件 /Users/xiexinfa/mcpmarket-quart/get_user_mcp_urls.py
"""

import asyncio
import sys
from src.user_mcp_urls import UserMCPURLManager, get_user_mcp_urls_list


async def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python get_user_mcp_urls.py <user_id> [--detailed]")
        print("示例: python get_user_mcp_urls.py 0992c0114e12600e43ef6fee2a1cd508")
        print("示例: python get_user_mcp_urls.py 0992c0114e12600e43ef6fee2a1cd508 --detailed")
        sys.exit(1)
    
    user_id = sys.argv[1]
    detailed = "--detailed" in sys.argv
    
    # 创建管理器
    manager = UserMCPURLManager()
    
    try:
        if detailed:
            # 详细输出
            urls = await manager.get_user_mcp_urls(user_id)
            print(manager.format_urls_output(urls))
        else:
            # 只输出URL列表
            url_list = await get_user_mcp_urls_list(user_id)
            for url in url_list:
                print(url)
        
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        return []


if __name__ == "__main__":
    asyncio.run(main())
