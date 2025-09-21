#!/usr/bin/env python3
"""
用户MCP服务器管理模块
用于查询和管理用户创建的MCP服务器实例
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from bson import ObjectId
from src.database import DatabaseManager
from src.config import config


class UserServerManager:
    """用户服务器管理器"""
    
    def __init__(self):
        self.db = DatabaseManager()
    
    async def get_user_servers(self, user_id: str, include_inactive: bool = False) -> List[Dict[str, Any]]:
        """
        获取用户创建的所有MCP服务器实例
        
        Args:
            user_id: 用户ID
            include_inactive: 是否包含非活跃实例
            
        Returns:
            用户服务器实例列表
        """
        await self.db.connect()
        
        try:
            # 构建查询条件
            query = {"user_id": user_id}
            if not include_inactive:
                query["status"] = "active"
            
            # 查询用户MCP实例
            instances = []
            cursor = self.db.user_mcp_instances_collection.find(query)
            async for instance in cursor:
                # 获取关联的服务器信息
                server_info = None
                server_id = instance.get('server_id')
                if server_id:
                    server_info = await self.db.servers_collection.find_one({'_id': ObjectId(server_id)})
                
                instances.append({
                    "_id": str(instance.get("_id")),
                    "instance_id": instance.get("instance_id"),
                    "instance_name": instance.get("instance_name", "Unknown"),
                    "server_id": str(server_id) if server_id else None,
                    "mcp_url": instance.get("mcp_url"),
                    "status": instance.get("status", "unknown"),
                    "auth_type": instance.get("auth_info", {}).get("type", "none"),
                    "selected_tools": instance.get("selected_tools", []),
                    "created_at": instance.get("created_at"),
                    "updated_at": instance.get("updated_at"),
                    "server_info": {
                        "name": server_info.get("name") if server_info else "Unknown",
                        "description": server_info.get("description", "") if server_info else "",
                        "url": server_info.get("url", "") if server_info else "",
                        "hosted": server_info.get("hosted", False) if server_info else False
                    } if server_info else None
                })
            
            return instances
            
        except Exception as e:
            print(f"❌ 获取用户服务器失败: {e}")
            raise
        finally:
            await self.db.close()
    
    async def get_user_server_urls(self, user_id: str, include_inactive: bool = False) -> List[str]:
        """
        获取用户创建的所有MCP服务器URL列表
        
        Args:
            user_id: 用户ID
            include_inactive: 是否包含非活跃实例
            
        Returns:
            MCP服务器URL列表
        """
        servers = await self.get_user_servers(user_id, include_inactive)
        urls = []
        
        for server in servers:
            if server.get("mcp_url"):
                urls.append(server["mcp_url"])
        
        return urls
    
    async def get_user_server_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        获取用户服务器统计信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            统计信息字典
        """
        await self.db.connect()
        
        try:
            # 查询所有实例
            all_instances = []
            cursor = self.db.user_mcp_instances_collection.find({"user_id": user_id})
            async for instance in cursor:
                all_instances.append(instance)
            
            # 统计状态分布
            status_count = {}
            for instance in all_instances:
                status = instance.get('status', 'unknown')
                status_count[status] = status_count.get(status, 0) + 1
            
            # 统计认证类型分布
            auth_type_count = {}
            for instance in all_instances:
                auth_type = instance.get('auth_info', {}).get('type', 'none')
                auth_type_count[auth_type] = auth_type_count.get(auth_type, 0) + 1
            
            # 统计工具选择情况
            total_tools = 0
            for instance in all_instances:
                total_tools += len(instance.get('selected_tools', []))
            
            return {
                "total_instances": len(all_instances),
                "active_instances": status_count.get('active', 0),
                "inactive_instances": len(all_instances) - status_count.get('active', 0),
                "status_distribution": status_count,
                "auth_type_distribution": auth_type_count,
                "total_tools_selected": total_tools,
                "average_tools_per_instance": total_tools / len(all_instances) if all_instances else 0
            }
            
        except Exception as e:
            print(f"❌ 获取统计信息失败: {e}")
            raise
        finally:
            await self.db.close()
    
    async def get_user_server_mappings(self, user_id: str) -> List[Dict[str, Any]]:
        """
        获取用户服务器映射信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            映射信息列表
        """
        await self.db.connect()
        
        try:
            mappings = []
            cursor = self.db.db.user_server_mappings.find({"user_id": user_id})
            async for mapping in cursor:
                mappings.append({
                    "_id": str(mapping.get("_id")),
                    "server_id": str(mapping.get("server_id")),
                    "instance_id": mapping.get("instance_id"),
                    "auth_type": mapping.get("auth_type"),
                    "created_at": mapping.get("created_at"),
                    "updated_at": mapping.get("updated_at")
                })
            
            return mappings
            
        except Exception as e:
            print(f"❌ 获取映射信息失败: {e}")
            raise
        finally:
            await self.db.close()
    
    async def print_user_servers_report(self, user_id: str, include_inactive: bool = False):
        """
        打印用户服务器详细报告
        
        Args:
            user_id: 用户ID
            include_inactive: 是否包含非活跃实例
        """
        print(f"🔍 查询用户 {user_id} 创建的MCP服务器实例")
        print(f"📊 数据库: {config.DATABASE_NAME}")
        print("=" * 80)
        
        try:
            # 获取服务器列表
            servers = await self.get_user_servers(user_id, include_inactive)
            
            if not servers:
                print("❌ 未找到任何服务器实例")
                return
            
            print(f"\n📋 找到 {len(servers)} 个服务器实例:")
            print("-" * 80)
            
            for i, server in enumerate(servers, 1):
                print(f"\n{i}. 实例信息:")
                print(f"   实例ID: {server.get('instance_id', 'N/A')}")
                print(f"   实例名称: {server.get('instance_name', 'N/A')}")
                print(f"   服务器ID: {server.get('server_id', 'N/A')}")
                print(f"   状态: {server.get('status', 'N/A')}")
                print(f"   认证类型: {server.get('auth_type', 'N/A')}")
                print(f"   选择工具: {len(server.get('selected_tools', []))} 个")
                print(f"   创建时间: {server.get('created_at', 'N/A')}")
                print(f"   更新时间: {server.get('updated_at', 'N/A')}")
                print(f"   MCP URL: {server.get('mcp_url', 'N/A')}")
                
                if server.get('server_info'):
                    server_info = server['server_info']
                    print(f"   关联服务器:")
                    print(f"     名称: {server_info.get('name', 'N/A')}")
                    print(f"     描述: {server_info.get('description', 'N/A')[:100]}...")
                    print(f"     是否托管: {server_info.get('hosted', False)}")
            
            # 获取统计信息
            stats = await self.get_user_server_statistics(user_id)
            print(f"\n📊 统计信息:")
            print(f"   总实例数: {stats['total_instances']}")
            print(f"   活跃实例: {stats['active_instances']}")
            print(f"   非活跃实例: {stats['inactive_instances']}")
            print(f"   选择工具总数: {stats['total_tools_selected']}")
            print(f"   平均每实例工具数: {stats['average_tools_per_instance']:.1f}")
            
            print(f"\n📈 状态分布:")
            for status, count in stats['status_distribution'].items():
                print(f"   {status}: {count} 个")
            
            print(f"\n🔐 认证类型分布:")
            for auth_type, count in stats['auth_type_distribution'].items():
                print(f"   {auth_type}: {count} 个")
            
            # 只显示URL列表
            print(f"\n🔗 所有MCP URL列表:")
            print("-" * 40)
            urls = await self.get_user_server_urls(user_id, include_inactive)
            for url in urls:
                print(url)
            
        except Exception as e:
            print(f"❌ 生成报告失败: {e}")
            import traceback
            traceback.print_exc()


async def main():
    """主函数 - 查询用户xray918的服务器"""
    user_id = "0992c0114e12600e43ef6fee2a1cd508"
    
    manager = UserServerManager()
    await manager.print_user_servers_report(user_id, include_inactive=True)


if __name__ == "__main__":
    asyncio.run(main())
