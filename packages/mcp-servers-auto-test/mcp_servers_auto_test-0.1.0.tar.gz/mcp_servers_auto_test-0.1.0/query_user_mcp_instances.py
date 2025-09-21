#!/usr/bin/env python3
"""
查询指定用户的MCP实例URL
"""
import asyncio
import sys
from src.database import DatabaseManager
from src.config import config

async def query_user_mcp_instances(user_id: str):
    """查询指定用户的所有MCP实例URL"""
    db = DatabaseManager()
    
    try:
        # 验证配置
        config.validate()
        
        # 连接数据库
        await db.connect()
        
        # 查询用户的MCP实例
        instances = await db.get_user_mcp_instances(user_id)
        
        if not instances:
            print(f"❌ 未找到用户 {user_id} 的MCP实例")
            return
        
        # 显示结果
        print(f"\n📋 用户 {user_id} 的MCP实例列表:")
        print("=" * 80)
        
        for i, instance in enumerate(instances, 1):
            print(f"\n{i}. 实例名称: {instance['name']}")
            print(f"   MCP URL: {instance['mcp_url']}")
            print(f"   描述: {instance['description']}")
            print(f"   创建时间: {instance.get('created_at', 'N/A')}")
            print(f"   更新时间: {instance.get('updated_at', 'N/A')}")
            print(f"   实例ID: {instance['_id']}")
        
        print(f"\n📊 总计找到 {len(instances)} 个MCP实例")
        
        # 只显示URL列表（用于复制）
        print(f"\n🔗 所有MCP URL列表:")
        print("-" * 40)
        for instance in instances:
            print(instance['mcp_url'])
        
    except Exception as e:
        print(f"❌ 查询失败: {e}")
    finally:
        await db.close()

def main():
    if len(sys.argv) != 2:
        print("用法: python query_user_mcp_instances.py <user_id>")
        print("示例: python query_user_mcp_instances.py 0992c0114e12600e43ef6fee2a1cd508")
        sys.exit(1)
    
    user_id = sys.argv[1]
    asyncio.run(query_user_mcp_instances(user_id))

if __name__ == "__main__":
    main()
