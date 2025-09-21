#!/usr/bin/env python3
import asyncio
import argparse
import signal
import sys
from pathlib import Path
from colorama import init
from src.config import config
from src.scheduler import TestScheduler
from src.database import DatabaseManager
from src.tester import ServerTester
from src.reporter import TestReporter

init(autoreset=True)

def signal_handler(signum, frame):
    """Handle system signals for graceful shutdown"""
    print(f"\n\n🛑 Received signal {signum}, shutting down gracefully...")
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


async def run_once(quick_mode: bool = False, server_name: str = None, test_mode: str = "parallel", proxy_mode: bool = False, user_id: str = None, local_mode: bool = False):
    """Run a single test cycle
    
    Args:
        quick_mode: If True, run quick test without LLM tool testing
        server_name: If provided, only test servers matching this name
        test_mode: Test execution mode - "parallel" or "serial"
        proxy_mode: If True, get URLs from user_mcp_instances (proxy URLs)
        user_id: User ID for proxy mode testing
        local_mode: If True, use local database instead of remote (default from .env)
    """
    mode = "QUICK" if quick_mode else "FULL"
    if server_name:
        print(f"Running single {mode} test for server: {server_name}")
    else:
        print(f"Running single {mode} test cycle...")
    
    db = DatabaseManager()
    tester = ServerTester()
    reporter = TestReporter()
    scheduler = TestScheduler()
    
    try:
        # Set database URI based on mode (hardcoded, not from .env)
        if local_mode:
            config.MONGODB_URI = "mongodb://mcpuser:Zhoubotong1@127.0.0.1:27017/mcpmarket?authSource=admin"
            print("🏠 Using local database: 127.0.0.1")
        else:
            # Use remote database (default)
            config.MONGODB_URI = "mongodb://mcpuser:Zhoubotong1@47.76.139.105:27017/mcpmarket"
            print("🌐 Using remote database: 47.76.139.105")
        
        # Validate configuration
        config.validate()
        
        # Get servers from database
        await db.connect()
        
        if proxy_mode:
            # Proxy mode: get URLs from user_mcp_instances with server names
            print(f"🔗 Proxy mode: Getting MCP URLs for user {user_id}")
            from src.user_mcp_urls import UserMCPURLManager
            manager = UserMCPURLManager()
            mcp_urls_info = await manager.get_user_mcp_urls(user_id)
            
            if not mcp_urls_info:
                print(f"❌ No active MCP instances found for user {user_id}")
                return
            
            # Convert URLs to server format with proper names
            servers = []
            for i, url_info in enumerate(mcp_urls_info):
                # Determine transport type based on URL
                transport = "streamable_http" if url_info['mcp_url'].startswith(('http://', 'https://')) else "sse"
                
                servers.append({
                    "_id": f"proxy_{i}",
                    "name": f"{url_info['server_name']} ({url_info['instance_name']})",
                    "mcp_url": url_info['mcp_url'],
                    "description": f"Proxy MCP server: {url_info['server_name']} - {url_info['instance_name']}",
                    "transport": transport
                })
            
            print(f"📊 Found {len(servers)} proxy MCP instances to test")
        else:
            # Normal mode: get hosted servers
            servers = await db.get_hosted_servers()
        
        # Filter servers if name is provided
        if server_name:
            # Filter servers by name (case-insensitive, partial match)
            filtered_servers = [
                s for s in servers 
                if server_name.lower() in s.get('name', '').lower()
            ]
            
            if not filtered_servers:
                print(f"❌ No servers found matching: {server_name}")
                available_names = list(set([
                    s.get('name', '').replace(' (SSE)', '').replace(' (Streamable HTTP)', '')
                    for s in servers
                ]))
                print(f"Available servers: {', '.join(sorted(available_names))}")
                return
            
            servers = filtered_servers
            print(f"📌 Found {len(servers)} server endpoint(s) matching '{server_name}'")
        
        if not servers:
            print("No hosted servers found in database")
            return
        
        # Run tests with the specified test mode
        if test_mode == "serial":
            print("🔄 Using serial testing mode")
        else:
            print("⚡ Using parallel testing mode")
        
        results = await tester.test_all_servers(servers, quick_mode, test_mode)
        
        # Generate reports
        scheduler.print_screen_report(results, mode)
        scheduler.append_to_md_report(results, mode)
        
        if not quick_mode:
            # Full test: save detailed reports and update database
            reporter.save_results(results)
            reporter.generate_html_report(results)
            
            for result in results:
                await db.update_server_test_result(result["server_id"], result)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Ensure proper cleanup
        try:
            await db.close()
        except Exception as e:
            print(f"⚠️ Warning: Error during database cleanup: {e}")
        
        # Give asyncio tasks time to clean up
        await asyncio.sleep(0.1)
        
   


async def run_scheduled(interval_minutes: int, test_mode: str = "parallel"):
    """Run tests on a schedule"""
    scheduler = TestScheduler(interval_minutes, test_mode)
    await scheduler.start()


def main():
    parser = argparse.ArgumentParser(
        description="MCP Servers Automated Testing Application"
    )
    parser.add_argument(
        "--mode",
        choices=["once", "scheduled", "once-quick", "single", "single-quick"],
        default="once-quick",
        help="Run mode: 'once' for full test all servers, 'once-quick' for quick test all servers, "
             "'single' for full test single server, 'single-quick' for quick test single server, "
             "'scheduled' for periodic testing (default: once-quick)"
    )
    parser.add_argument(
        "--server",
        type=str,
        help="Server name to test (for 'single' and 'single-quick' modes). Supports partial match."
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=30,
        help="Quick test interval in minutes for scheduled mode (default: 30)"
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        default=True,
        help="Use parallel testing mode (default: True)"
    )
    parser.add_argument(
        "--serial",
        action="store_true",
        help="Use serial testing mode (overrides --parallel)"
    )
    parser.add_argument(
        "--proxy",
        action="store_true",
        default=True,
        help="Test MCP servers through proxy (get URLs from user_mcp_instances instead of hosted servers) - default: True"
    )
    parser.add_argument(
        "--no-proxy",
        action="store_true",
        help="Disable proxy mode and use direct hosted servers"
    )
    parser.add_argument(
        "--user-id",
        type=str,
        default="0992c0114e12600e43ef6fee2a1cd508",
        help="User ID for proxy mode testing (default: 0992c0114e12600e43ef6fee2a1cd508)"
    )
    parser.add_argument(
        "--remote",
        action="store_true",
        help="Use remote database (47.76.139.105) - this is the default"
    )
    parser.add_argument(
        "--local",
        action="store_true",
        help="Use local database (127.0.0.1) instead of remote database"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="mcp-servers-auto-test 0.1.3"
    )
    
    args = parser.parse_args()
    
    print("""
╔═══════════════════════════════════════════════════════════╗
║         MCP Servers Automated Testing Application         ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Handle test mode logic
    if args.serial:
        test_mode = "serial"
        print("🔄 Using serial testing mode")
    else:
        test_mode = "parallel"
        print("⚡ Using parallel testing mode")
    
    # Handle proxy mode logic
    # If local mode is specified, default to no-proxy unless explicitly requested
    if args.local and not args.no_proxy:
        # Check if proxy was explicitly requested via command line
        import sys
        if "--proxy" in sys.argv:
            proxy_mode = True
            print("🔗 Proxy mode enabled - testing through user MCP instances")
        else:
            proxy_mode = False
            print("🔗 Local mode: Using direct hosted servers (local database has different user IDs)")
    else:
        proxy_mode = args.proxy and not args.no_proxy
        if proxy_mode:
            print("🔗 Proxy mode enabled - testing through user MCP instances")
        elif args.no_proxy:
            print("🔗 Direct mode enabled - testing hosted servers directly")
    
    try:
        if args.mode == "once":
            asyncio.run(run_once(quick_mode=False, server_name=args.server, test_mode=test_mode, proxy_mode=proxy_mode, user_id=args.user_id, local_mode=args.local))
        elif args.mode == "once-quick":
            asyncio.run(run_once(quick_mode=True, server_name=args.server, test_mode=test_mode, proxy_mode=proxy_mode, user_id=args.user_id, local_mode=args.local))
        elif args.mode == "single":
            if not args.server:
                print("❌ Error: --server parameter is required for 'single' mode")
                parser.print_help()
                return
            asyncio.run(run_once(quick_mode=False, server_name=args.server, test_mode=test_mode, proxy_mode=proxy_mode, user_id=args.user_id, local_mode=args.local))
        elif args.mode == "single-quick":
            if not args.server:
                print("❌ Error: --server parameter is required for 'single-quick' mode")
                parser.print_help()
                return
            asyncio.run(run_once(quick_mode=True, server_name=args.server, test_mode=test_mode, proxy_mode=proxy_mode, user_id=args.user_id, local_mode=args.local))
        else:
            asyncio.run(run_scheduled(args.interval, test_mode))
    except KeyboardInterrupt:
        print("\n\nTest application stopped by user")
    except Exception as e:
        print(f"\nFatal error: {e}")
    finally:
        # Ensure all pending tasks are cleaned up
        try:
            # Get all running tasks
            loop = asyncio.get_event_loop()
            if loop and not loop.is_closed():
                # Cancel all pending tasks
                pending = asyncio.all_tasks(loop)
                for task in pending:
                    task.cancel()
                # Wait for cancellation to complete
                loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                loop.close()
        except:
            pass  # Ignore cleanup errors



if __name__ == "__main__":
    main()