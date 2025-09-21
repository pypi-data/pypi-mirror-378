#!/bin/bash

# MCP Servers Auto Test - Public Installation Script
# This script installs the mcp-test command from a private GitHub repository

set -e

echo "🚀 Installing MCP Servers Auto Test..."

# Check if Python 3.10+ is available
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python 3.10+ is required. Current version: $python_version"
    echo "Please install Python 3.10 or later and try again."
    exit 1
fi

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Check if git is available
if ! command -v git &> /dev/null; then
    echo "❌ Error: Git is required to clone the private repository."
    echo "Please install Git and try again."
    exit 1
fi

# Clone and install
echo "📦 Cloning private repository..."
if [ -d "mcp-servers-auto-test" ]; then
    echo "📁 Directory exists, updating..."
    cd mcp-servers-auto-test
    git pull
else
    git clone https://github.com/xray918/mcp-servers-auto-test.git
    cd mcp-servers-auto-test
fi

echo "📦 Installing mcp-test..."
uv tool install .

# Verify installation
if command -v mcp-test &> /dev/null; then
    echo "✅ mcp-test installed successfully!"
    echo "📍 Location: $(which mcp-test)"
    echo ""
    echo "🎉 You can now use 'mcp-test' command from anywhere!"
    echo ""
    echo "📖 Usage examples:"
    echo "  mcp-test                    # Run default test (remote, proxy, parallel, quick)"
    echo "  mcp-test --help             # Show help"
    echo "  mcp-test --server github    # Test specific server"
    echo "  mcp-test --local            # Use local database"
    echo "  mcp-test --serial           # Use serial testing"
    echo ""
    echo "🔧 To uninstall: uv tool uninstall mcp-servers-auto-test"
    echo "🗑️  To clean up: rm -rf mcp-servers-auto-test"
else
    echo "❌ Installation failed. Please check the error messages above."
    exit 1
fi
