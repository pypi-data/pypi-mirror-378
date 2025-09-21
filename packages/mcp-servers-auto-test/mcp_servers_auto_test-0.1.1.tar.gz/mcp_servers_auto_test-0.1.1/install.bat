@echo off
REM MCP Test Application Installation Script for Windows
echo 🚀 Installing MCP Test Application...

REM Check if uv is installed
uv --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: uv is not installed. Please install uv first:
    echo    Visit: https://docs.astral.sh/uv/getting-started/installation/
    pause
    exit /b 1
)

REM Check if Python 3.10+ is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: Python is not installed or not in PATH
    echo    Please install Python 3.10 or higher from https://python.org
    pause
    exit /b 1
)

echo ✅ Python check passed

REM Install the application in development mode
echo 📦 Installing application in development mode...
uv pip install -e .

if %errorlevel% equ 0 (
    echo ✅ Installation successful!
    echo.
    echo 🎉 You can now use the 'mcp-test' command from any directory!
    echo.
    echo Usage examples:
    echo   mcp-test --help                    # Show help
    echo   mcp-test --mode once               # Run single full test
    echo   mcp-test --mode once-quick         # Run single quick test
    echo   mcp-test --mode single --server 滴滴打车  # Test specific server
    echo   mcp-test --mode scheduled          # Run scheduled testing
    echo.
    echo 📚 For more information, run: mcp-test --help
) else (
    echo ❌ Installation failed. Please check the error messages above.
    pause
    exit /b 1
)

pause
