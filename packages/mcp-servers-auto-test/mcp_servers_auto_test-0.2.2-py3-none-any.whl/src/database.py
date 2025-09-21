import asyncio
from typing import List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
from bson import ObjectId
from src.config import config


class DatabaseManager:
    def __init__(self):
        self.client = None
        self.db = None
        self.servers_collection = None
        self.user_mcp_instances_collection = None
    
    async def connect(self):
        try:
            print(f"🔌 Attempting to connect to MongoDB...")
            print(f"   URI: {config.MONGODB_URI[:50]}...")
            
            self.client = AsyncIOMotorClient(config.MONGODB_URI)
            await self.client.admin.command('ping')
            self.db = self.client[config.DATABASE_NAME]
            self.servers_collection = self.db[config.SERVERS_COLLECTION]
            self.user_mcp_instances_collection = self.db["user_mcp_instances"]
            print(f"✅ Connected to MongoDB database: {config.DATABASE_NAME}")
        except ConnectionFailure as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            print(f"   Please check your MONGODB_URI in the .env file")
            print(f"   Current URI: {config.MONGODB_URI}")
            raise
        except Exception as e:
            print(f"❌ Unexpected error connecting to MongoDB: {e}")
            print(f"   Please check your MONGODB_URI format in the .env file")
            raise
    
    async def get_hosted_servers(self) -> List[Dict[str, Any]]:
        if self.servers_collection is None:
            await self.connect()
        
        try:
            servers = []
            cursor = self.servers_collection.find({"hosted": True})
            async for server in cursor:
                if "mcp_url" in server and server["mcp_url"]:
                    mcp_url = server["mcp_url"]
                    
                    # Handle different mcp_url formats
                    if isinstance(mcp_url, dict):
                        # Add both SSE and Streamable HTTP URLs if they exist
                        if "sse_url" in mcp_url and mcp_url["sse_url"]:
                            servers.append({
                                "_id": str(server.get("_id")),
                                "name": server.get("name", "Unknown") + " (SSE)",
                                "mcp_url": mcp_url["sse_url"],
                                "description": server.get("description", ""),
                                "transport": "sse"
                            })
                        
                        if "streamable_http_url" in mcp_url and mcp_url["streamable_http_url"]:
                            servers.append({
                                "_id": str(server.get("_id")),
                                "name": server.get("name", "Unknown") + " (Streamable HTTP)",
                                "mcp_url": mcp_url["streamable_http_url"],
                                "description": server.get("description", ""),
                                "transport": "streamable_http"
                            })
                    else:
                        # Assume it's a string URL
                        servers.append({
                            "_id": str(server.get("_id")),
                            "name": server.get("name", "Unknown"),
                            "mcp_url": mcp_url,
                            "description": server.get("description", ""),
                            "transport": server.get("transport", "sse")
                        })
            
            print(f"📊 Found {len(servers)} server endpoints to test")
            return servers
        except Exception as e:
            print(f"❌ Error fetching servers: {e}")
            raise
    
    async def update_server_test_result(self, server_id: str, test_result: Dict[str, Any]):
        if self.servers_collection is None:
            await self.connect()
        
        try:
            # Convert string ID back to ObjectId for MongoDB query
            if isinstance(server_id, str):
                server_id = ObjectId(server_id)
            
            await self.servers_collection.update_one(
                {"_id": server_id},
                {"$set": {"last_test_result": test_result}}
            )
        except Exception as e:
            print(f"❌ Error updating test result for server {server_id}: {e}")
    
    async def get_user_mcp_instances(self, user_id: str) -> List[Dict[str, Any]]:
        """获取指定用户的所有MCP实例URL"""
        if self.user_mcp_instances_collection is None:
            await self.connect()
        
        try:
            instances = []
            cursor = self.user_mcp_instances_collection.find({"user_id": user_id})
            async for instance in cursor:
                if "mcp_url" in instance and instance["mcp_url"]:
                    instances.append({
                        "_id": str(instance.get("_id")),
                        "user_id": instance.get("user_id"),
                        "mcp_url": instance["mcp_url"],
                        "name": instance.get("name", "Unknown"),
                        "description": instance.get("description", ""),
                        "created_at": instance.get("created_at"),
                        "updated_at": instance.get("updated_at")
                    })
            
            print(f"📊 Found {len(instances)} MCP instances for user: {user_id}")
            return instances
        except Exception as e:
            print(f"❌ Error fetching user MCP instances: {e}")
            raise
    
    async def close(self):
        if self.client:
            self.client.close()
            print("🔌 Disconnected from MongoDB")