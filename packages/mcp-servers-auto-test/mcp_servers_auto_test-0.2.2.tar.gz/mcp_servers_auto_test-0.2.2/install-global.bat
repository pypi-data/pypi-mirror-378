@echo off
REM MCP Servers Auto Test - Global Installation Script for Windows
REM This script installs the mcp-test command globally on Windows

echo 🚀 Installing MCP Servers Auto Test globally...

REM Check if Python 3.10+ is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://python.org and try again.
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set python_version=%%i
echo Found Python version: %python_version%

REM Check if uv is installed
uv --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 📦 Installing uv package manager...
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    if %errorlevel% neq 0 (
        echo ❌ Failed to install uv. Please install manually from https://github.com/astral-sh/uv
        pause
        exit /b 1
    )
)

REM Install the package globally
echo 📦 Installing mcp-test globally with uv...
uv tool install .

REM Verify installation
mcp-test --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ mcp-test installed successfully!
    echo.
    echo 🎉 You can now use 'mcp-test' command from anywhere!
    echo.
    echo 📖 Usage examples:
    echo   mcp-test                    # Run default test (remote, proxy, parallel, quick)
    echo   mcp-test --help             # Show help
    echo   mcp-test --server github    # Test specific server
    echo   mcp-test --local            # Use local database
    echo   mcp-test --serial           # Use serial testing
    echo.
    echo 🔧 To uninstall: uv tool uninstall mcp-servers-auto-test
) else (
    echo ❌ Installation failed. Please check the error messages above.
    pause
    exit /b 1
)

pause