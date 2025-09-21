# MCP服务器自动测试系统

一个基于Model Context Protocol (MCP)的自动化测试系统，用于测试各种MCP服务器的连接性和功能。

## 🚀 快速开始

### 全局安装（推荐）

让 `mcp-test` 命令在任何地方都能使用：

#### 方法1: 从私有仓库安装

**Linux/macOS:**
```bash
# 克隆私有仓库并安装
git clone https://github.com/xray918/mcp-servers-auto-test.git
cd mcp-servers-auto-test

# 安装uv（如果没有）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 全局安装
uv tool install .

# 验证安装
mcp-test --help
```

**Windows:**
```cmd
# 克隆私有仓库
git clone https://github.com/xray918/mcp-servers-auto-test.git
cd mcp-servers-auto-test

# 安装uv（如果没有）
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 全局安装
uv tool install .

# 验证安装
mcp-test --help
```

#### 方法2: 直接使用uv安装

```bash
# 安装uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 从GitHub直接安装（需要GitHub访问权限）
uv tool install git+https://github.com/xray918/mcp-servers-auto-test.git

# 验证安装
mcp-test --help
```

#### 方法3: 本地开发安装

```bash
# 克隆项目
git clone https://github.com/xray918/mcp-servers-auto-test.git
cd mcp-servers-auto-test

# 安装依赖
uv pip install -e .

# 运行
uv run python main.py
```

### 卸载

```bash
# 卸载全局安装的mcp-test
uv tool uninstall mcp-servers-auto-test
```

## 📖 操作b

### 默认行为
系统默认使用以下配置（无需任何参数）：
- **🌐 远程数据库**：`47.76.139.105:27017`
- **🔗 Proxy模式**：从用户MCP实例获取URL
- **⚡ 并行测试**：使用并行模式执行测试
- **🎯 一次运行**：`once-quick` 模式（快速测试一次）
- **🚀 快速模式**：QUICK模式，不进行LLM工具调用测试

### 基本测试指令

```bash
# 默认测试（远程数据库 + Proxy模式 + 并行 + 快速）
mcp-test

# 显示帮助信息
mcp-test --help
```

### 数据库模式

```bash
# 使用远程数据库（默认）
mcp-test

# 使用本地数据库（自动切换到直接模式）
mcp-test --local

# 明确指定远程数据库
mcp-test --remote
```

### 测试模式

```bash
# 并行测试（默认）
mcp-test

# 串行测试
mcp-test --serial

# 完整测试（包含LLM工具调用）
mcp-test --mode once

# 快速测试（默认）
mcp-test --mode once-quick
```

### 服务器选择

```bash
# 测试所有服务器（默认）
mcp-test

# 测试特定服务器
mcp-test --mode single --server github

# 测试特定服务器（快速模式）
mcp-test --mode single-quick --server github
```

### 代理模式

```bash
# Proxy模式（默认，从用户MCP实例获取URL）
mcp-test

# 直接模式（从托管服务器获取URL）
mcp-test --no-proxy

# 本地数据库 + 直接模式（自动组合）
mcp-test --local

# 本地数据库 + Proxy模式（明确指定）
mcp-test --local --proxy
```

### 调度测试

```bash
# 定时测试（每30分钟）
mcp-test --mode scheduled

# 自定义间隔（60分钟）
mcp-test --mode scheduled --interval 60
```

### 常用组合示例

```bash
# 1. 默认测试（推荐）
mcp-test

# 2. 本地环境测试
mcp-test --local

# 3. 串行测试（调试用）
mcp-test --serial

# 4. 完整测试（包含LLM调用）
mcp-test --mode once

# 5. 测试特定服务器
mcp-test --mode single --server github

# 6. 本地 + 直接模式
mcp-test --local --no-proxy

# 7. 本地 + Proxy模式
mcp-test --local --proxy

# 8. 远程 + 直接模式
mcp-test --no-proxy

# 9. 定时测试
mcp-test --mode scheduled --interval 60
```

## 📋 功能特性

- **多协议支持**: 支持SSE和Streamable HTTP两种MCP传输协议
- **智能测试**: 使用OpenAI API生成真实的测试参数
- **异常处理**: 强大的异常处理机制，确保程序稳定运行
- **详细报告**: 生成HTML和Markdown格式的测试报告
- **数据库集成**: 自动保存测试结果到MongoDB
- **调度执行**: 支持定时自动测试

## 🛠️ 配置

在运行前，请确保设置以下环境变量：

```bash
# MongoDB连接
export MONGODB_URI="mongodb://localhost:27017"
export DATABASE_NAME="mcp_servers"
export SERVERS_COLLECTION="servers"

# OpenAI API（用于生成测试参数）
export OPENAI_API_KEY="your-openai-api-key"

# 测试超时设置
export DEFAULT_TIMEOUT=30
export SSE_READ_TIMEOUT=60

# 并行测试配置
export QUICK_MODE_MAX_CONCURRENT=5    # 快速模式最大并发数
export FULL_MODE_MAX_CONCURRENT=3     # 完整模式最大并发数
```

## 📁 项目结构

```
```