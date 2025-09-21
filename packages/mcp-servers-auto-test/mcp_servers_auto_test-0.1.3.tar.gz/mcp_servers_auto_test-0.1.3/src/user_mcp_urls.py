#!/usr/bin/env python3
"""
获取用户所有活跃MCP实例的URL模块
基于参考文件 /Users/xiexinfa/mcpmarket-quart/get_user_mcp_urls.py
"""

import asyncio
from typing import List, Dict, Any
from bson import ObjectId
from src.database import DatabaseManager
from src.config import config


class UserMCPURLManager:
    """用户MCP URL管理器"""
    
    def __init__(self):
        """初始化MCP URL管理器"""
        self.db = DatabaseManager()
    
    async def get_user_active_instances(self, user_id: str) -> List[Dict[str, Any]]:
        """
        获取用户所有活跃的MCP实例
        
        Args:
            user_id: 用户ID
            
        Returns:
            活跃实例列表
        """
        await self.db.connect()
        
        try:
            # 查询活跃实例
            instances = []
            cursor = self.db.user_mcp_instances_collection.find({
                'user_id': user_id,
                'status': 'active'
            }).sort('created_at', -1)
            
            async for instance in cursor:
                instances.append(instance)
            
            if not instances:
                return []
            
            # 获取服务器信息
            server_ids = list(set(str(instance['server_id']) for instance in instances if instance.get('server_id')))
            servers = []
            if server_ids:
                cursor = self.db.servers_collection.find({
                    '_id': {'$in': [ObjectId(sid) for sid in server_ids]}
                })
                async for server in cursor:
                    servers.append(server)
            
            # 创建服务器信息映射
            servers_dict = {str(server['_id']): server for server in servers}
            
            # 补充服务器信息到实例中
            for instance in instances:
                server_id = str(instance.get('server_id', ''))
                server = servers_dict.get(server_id, {})
                instance['server_info'] = {
                    'name': server.get('name', 'Unknown'),
                    'alias': server.get('alias', 'Unknown'),
                    'description': server.get('description', 'No description')
                }
            
            return instances
            
        except Exception as e:
            print(f"❌ 获取用户实例失败: {e}")
            return []
        finally:
            await self.db.close()
    
    async def get_user_mcp_urls(self, user_id: str) -> List[Dict[str, str]]:
        """
        获取用户所有活跃实例的MCP URL
        
        Args:
            user_id: 用户ID
            
        Returns:
            MCP URL列表，包含实例名称和URL
        """
        instances = await self.get_user_active_instances(user_id)
        
        urls = []
        for instance in instances:
            server_info = instance.get('server_info', {})
            urls.append({
                'instance_name': instance.get('instance_name', 'Unknown'),
                'server_name': server_info.get('name', 'Unknown'),
                'mcp_url': instance.get('mcp_url', 'No URL'),
                'tool_count': len(instance.get('selected_tools', [])),
                'auth_type': instance.get('auth_info', {}).get('type', 'none'),
                'created_at': instance.get('created_at', 'Unknown')
            })
        
        return urls
    
    def get_urls_only(self, urls: List[Dict[str, str]]) -> List[str]:
        """
        仅获取MCP URL列表
        
        Args:
            urls: URL列表
            
        Returns:
            仅包含URL的列表
        """
        return [url_info['mcp_url'] for url_info in urls if url_info['mcp_url'] != 'No URL']
    
    def format_urls_output(self, urls: List[Dict[str, str]]) -> str:
        """
        格式化URL输出
        
        Args:
            urls: URL列表
            
        Returns:
            格式化的字符串
        """
        if not urls:
            return "❌ 未找到活跃的MCP实例"
        
        output = []
        output.append("=" * 80)
        output.append(f"用户活跃MCP实例URL列表 (共{len(urls)}个)")
        output.append("=" * 80)
        
        for i, url_info in enumerate(urls, 1):
            output.append(f"\n{i}. {url_info['instance_name']} ({url_info['server_name']})")
            output.append(f"   MCP URL: {url_info['mcp_url']}")
            output.append(f"   工具数: {url_info['tool_count']} 个")
            output.append(f"   认证类型: {url_info['auth_type']}")
            output.append(f"   创建时间: {url_info['created_at']}")
        
        output.append("\n" + "=" * 80)
        return "\n".join(output)


async def get_user_mcp_urls_list(user_id: str) -> List[str]:
    """
    获取用户MCP URLs的简化函数
    
    Args:
        user_id: 用户ID
        
    Returns:
        MCP URL列表
    """
    manager = UserMCPURLManager()
    urls = await manager.get_user_mcp_urls(user_id)
    return manager.get_urls_only(urls)


async def main():
    """主函数 - 获取用户xray918的MCP URLs"""
    user_id = '0992c0114e12600e43ef6fee2a1cd508'
    
    # 创建管理器
    manager = UserMCPURLManager()
    
    try:
        # 获取用户MCP URLs
        urls = await manager.get_user_mcp_urls(user_id)
        
        # 只输出URL列表
        url_list = manager.get_urls_only(urls)
        for url in url_list:
            print(url)
        
        return url_list
        
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        return []


if __name__ == "__main__":
    asyncio.run(main())
