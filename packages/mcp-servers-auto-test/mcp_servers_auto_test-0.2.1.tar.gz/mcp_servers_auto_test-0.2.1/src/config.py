import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()


class Config:
    # 数据库URI将在运行时动态设置，不依赖环境变量
    MONGODB_URI: str = ""
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    DEFAULT_TIMEOUT: int = int(os.getenv("DEFAULT_TIMEOUT", "3"))
    SSE_READ_TIMEOUT: int = int(os.getenv("SSE_READ_TIMEOUT", "6"))
    
    # 并行测试配置
    # 降低并发度以避免TypeScript gateway的并发限制
    QUICK_MODE_MAX_CONCURRENT: int = int(os.getenv("QUICK_MODE_MAX_CONCURRENT", "3"))
    FULL_MODE_MAX_CONCURRENT: int = int(os.getenv("FULL_MODE_MAX_CONCURRENT", "2"))
    
    # 测试模式配置
    DEFAULT_TEST_MODE: str = os.getenv("DEFAULT_TEST_MODE", "parallel")  # "parallel" 或 "serial"
    
    DATABASE_NAME: str = "mcpmarket"
    SERVERS_COLLECTION: str = "servers"
    
    @classmethod
    def validate(cls) -> bool:
        # MONGODB_URI 现在在运行时动态设置，不需要从环境变量检查
        if not cls.MONGODB_URI:
            raise ValueError("MONGODB_URI is not set. This should be set dynamically by the application.")
        
        # Validate MongoDB URI format
        if not cls.MONGODB_URI.startswith(('mongodb://', 'mongodb+srv://')):
            raise ValueError("MONGODB_URI must start with 'mongodb://' or 'mongodb+srv://'")
        
        # Check for common URI format issues
        if ' ' in cls.MONGODB_URI:
            raise ValueError("MONGODB_URI contains spaces. Please check the URI format")
        
        if not cls.OPENAI_API_KEY:
            print("Warning: OPENAI_API_KEY not set, tool testing will be limited")
        return True


config = Config()