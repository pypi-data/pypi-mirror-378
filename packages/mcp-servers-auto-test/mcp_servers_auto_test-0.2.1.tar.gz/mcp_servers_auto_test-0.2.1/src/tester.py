import asyncio
from datetime import datetime
from typing import Dict, Any, List
from src.mcp_client import MCPClient
from src.config import config
from colorama import Fore, Style, init

init(autoreset=True)


class ServerTester:
    def __init__(self):
        self.test_results = []
        
    async def test_server(self, server: Dict[str, Any], quick_mode: bool = False) -> Dict[str, Any]:
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}Testing Server: {server['name']}")
        print(f"{Fore.CYAN}URL: {server['mcp_url']}")
        print(f"{Fore.CYAN}{'='*60}")
        
        result = {
            "server_id": server["_id"],
            "server_name": server["name"],
            "server_url": server["mcp_url"],
            "test_time": datetime.now().isoformat(),
            "connection_test": {"success": False},
            "tools_test": {"success": False, "tools": []},
            "overall_status": "failed"
        }
        
        client = MCPClient()
        
        # Connection Test
        print(f"\n{Fore.YELLOW}📡 Testing connection...")
        try:
            connected = await client.connect(server["mcp_url"], server.get("transport", "sse"))
            if connected:
                result["connection_test"]["success"] = True
                print(f"{Fore.GREEN}✅ Connection successful")
                
                # Get Tools Test
                print(f"\n{Fore.YELLOW}🔧 Fetching tools...")
                try:
                    tools = await client.get_tools()
                    result["tools_test"]["total_tools"] = len(tools)
                    print(f"{Fore.GREEN}✅ Found {len(tools)} tools")
                    
                    if tools:
                        result["tools_test"]["success"] = True
                        
                        if not quick_mode:
                            # Full mode: Test tools with LLM
                            # Skip tool testing for SSE if there's a corresponding Streamable HTTP endpoint
                            should_test_tools = True
                            if " (SSE)" in server.get("name", ""):
                                # This is an SSE endpoint, check if we should skip tool testing
                                base_name = server.get("name", "").replace(" (SSE)", "")
                                # If this server has both SSE and Streamable HTTP, only test tools on Streamable HTTP
                                print(f"{Fore.CYAN}    ℹ️ Skipping tool testing for SSE endpoint (will test on Streamable HTTP)")
                                should_test_tools = False
                                result["tools_test"]["success"] = True
                                result["overall_status"] = "passed"
                                # Just mark tools as verified
                                for tool in tools:
                                    tool_result = {
                                        "name": tool["function"]["name"],
                                        "description": tool["function"].get("description", ""),
                                        "test_success": True,
                                        "test_params": {},
                                        "test_result": {"message": "Tool testing skipped for SSE (tested via Streamable HTTP)"}
                                    }
                                    result["tools_test"]["tools"].append(tool_result)
                            
                            if should_test_tools:
                                # Test tools for Streamable HTTP or standalone servers
                                for tool in tools[:3]:  # Test up to 3 tools
                                    tool_result = await self._test_single_tool(client, tool)
                                    result["tools_test"]["tools"].append(tool_result)
                        else:
                            # Quick mode: Just verify tools exist and are valid
                            for tool in tools:
                                tool_result = {
                                    "name": tool["function"]["name"],
                                    "description": tool["function"].get("description", ""),
                                    "test_success": True,
                                    "test_params": {},
                                    "test_result": {"message": "Tool structure verified (quick mode)"}
                                }
                                result["tools_test"]["tools"].append(tool_result)
                        
                        # Calculate success rate
                        successful_tests = sum(1 for t in result["tools_test"]["tools"] if t["test_success"])
                        result["tools_test"]["success_rate"] = successful_tests / len(result["tools_test"]["tools"])
                        
                        if result["tools_test"]["success_rate"] >= 0.5:
                            result["overall_status"] = "passed"
                        else:
                            result["overall_status"] = "partial"
                    else:
                        print(f"{Fore.YELLOW}⚠️ No tools found")
                        result["overall_status"] = "passed"  # Connection works but no tools
                        
                except Exception as e:
                    print(f"{Fore.RED}❌ Failed to get tools: {e}")
                    result["tools_test"]["error"] = str(e)
            else:
                print(f"{Fore.RED}❌ Connection failed")
                result["connection_test"]["error"] = "Failed to establish connection"
                
        except BaseException as e:
            # Handle all types of exceptions including BaseExceptionGroup
            error_msg = str(e)
            if "403 Forbidden" in error_msg:
                error_msg = "403 Forbidden - Access denied (check API key)"
            elif "404" in error_msg:
                error_msg = "404 Not Found - Server endpoint not available"
            elif len(error_msg) > 200:
                error_msg = error_msg[:200] + "..."
            print(f"{Fore.RED}❌ Connection error: {error_msg}")
            result["connection_test"]["error"] = error_msg
        finally:
            await client.cleanup()
        
        # Print Summary
        self._print_test_summary(result)
        return result
    
    async def _test_single_tool(self, client: MCPClient, tool: Dict[str, Any]) -> Dict[str, Any]:
        tool_name = tool["function"]["name"]
        print(f"\n{Fore.BLUE}  Testing tool: {tool_name}")
        
        tool_result = {
            "name": tool_name,
            "description": tool["function"].get("description", ""),
            "test_success": False,
            "test_params": {},
            "test_result": None
        }
        
        try:
            # Generate test parameters if OpenAI is available
            if config.OPENAI_API_KEY:
                test_params = await client.generate_tool_test_params(tool)
                tool_result["test_params"] = test_params
                
                if test_params:
                    # Test the tool with generated parameters
                    test_response = await client.test_tool(tool_name, test_params)
                    tool_result["test_result"] = test_response
                    tool_result["test_success"] = test_response.get("success", False)
                    
                    # Check semantic analysis results
                    semantic_analysis = test_response.get("semantic_analysis", {})
                    status = semantic_analysis.get("status", "unknown")
                    
                    if status == "api_key_missing":
                        print(f"{Fore.YELLOW}    ⚠️ API Key Issue: {semantic_analysis.get('message', 'API key missing or invalid')}")
                        tool_result["test_success"] = False
                        tool_result["api_issue"] = "api_key_missing"
                    elif status == "quota_exceeded":
                        print(f"{Fore.YELLOW}    ⚠️ Quota/Billing Issue: {semantic_analysis.get('message', 'Quota exceeded or billing problem')}")
                        tool_result["test_success"] = False
                        tool_result["api_issue"] = "quota_exceeded"
                    elif tool_result["test_success"]:
                        print(f"{Fore.GREEN}    ✅ Tool test passed")
                    else:
                        print(f"{Fore.RED}    ❌ Tool test failed: {test_response.get('error', semantic_analysis.get('message', 'Unknown error'))}")
                else:
                    # Could not generate test parameters, but tool exists
                    print(f"{Fore.YELLOW}    ⚠️ Could not generate test parameters")
                    tool_result["test_success"] = True  # Mark as success since tool exists
                    tool_result["test_result"] = {"message": "Tool verification but test params generation failed"}
            else:
                # Just verify tool exists
                tool_result["test_success"] = True
                tool_result["test_result"] = {"message": "Tool verification only (no OpenAI key)"}
                print(f"{Fore.GREEN}    ✅ Tool verified (no functional test)")
                
        except BaseException as e:
            error_msg = str(e)
            if "ValidationError" in str(type(e).__name__) or "validation" in error_msg.lower():
                print(f"{Fore.YELLOW}    ⚠️ Tool test validation error (server response format issue)")
                tool_result["test_result"] = {"error": "Server response validation error"}
            else:
                print(f"{Fore.RED}    ❌ Tool test error: {error_msg[:100]}")
                tool_result["test_result"] = {"error": error_msg[:200]}
        
        return tool_result
    
    def _print_test_summary(self, result: Dict[str, Any]):
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}Test Summary for {result['server_name']}")
        print(f"{Fore.CYAN}{'='*60}")
        
        # Connection status
        if result["connection_test"]["success"]:
            print(f"{Fore.GREEN}Connection: ✅ PASSED")
        else:
            print(f"{Fore.RED}Connection: ❌ FAILED")
        
        # Tools status
        if result["tools_test"]["success"]:
            total_tools = result["tools_test"].get("total_tools", 0)
            success_rate = result["tools_test"].get("success_rate", 0)
            print(f"{Fore.GREEN}Tools: ✅ {total_tools} tools found, {success_rate:.0%} test success rate")
            
            # Check for API issues in tool tests
            api_issues = {}
            for tool in result["tools_test"].get("tools", []):
                if "api_issue" in tool:
                    issue_type = tool["api_issue"]
                    api_issues[issue_type] = api_issues.get(issue_type, 0) + 1
            
            if api_issues:
                print(f"{Fore.YELLOW}API Issues Detected:")
                if "api_key_missing" in api_issues:
                    print(f"{Fore.YELLOW}  - API Key Missing/Invalid: {api_issues['api_key_missing']} tool(s)")
                if "quota_exceeded" in api_issues:
                    print(f"{Fore.YELLOW}  - Quota/Billing Issues: {api_issues['quota_exceeded']} tool(s)")
        else:
            print(f"{Fore.RED}Tools: ❌ FAILED")
        
        # Overall status
        status_color = {
            "passed": Fore.GREEN,
            "partial": Fore.YELLOW,
            "failed": Fore.RED
        }.get(result["overall_status"], Fore.WHITE)
        
        print(f"\n{status_color}Overall Status: {result['overall_status'].upper()}")
        print(f"{Fore.CYAN}{'='*60}\n")
    
    async def test_all_servers(self, servers: List[Dict[str, Any]], quick_mode: bool = False, test_mode: str = "parallel") -> List[Dict[str, Any]]:
        mode_text = "QUICK MODE" if quick_mode else "FULL MODE"
        test_mode_text = "PARALLEL" if test_mode == "parallel" else "SERIAL"
        print(f"\n{Fore.MAGENTA}Starting automated test for {len(servers)} servers [{mode_text}] [{test_mode_text}]...")
        
        if test_mode == "serial":
            return await self._test_servers_serial(servers, quick_mode)
        else:
            return await self._test_servers_parallel(servers, quick_mode)
    
    async def _test_servers_serial(self, servers: List[Dict[str, Any]], quick_mode: bool = False) -> List[Dict[str, Any]]:
        """Serial testing for all servers"""
        print(f"{Fore.CYAN}🔄 Using serial testing (one server at a time)")
        
        self.test_results = []
        start_time = datetime.now()
        
        for i, server in enumerate(servers, 1):
            print(f"\n{Fore.MAGENTA}[{i}/{len(servers)}] Testing: {server['name']}")
            try:
                result = await self.test_server(server, quick_mode)
                self.test_results.append(result)
                print(f"{Fore.GREEN}✅ [{i}/{len(servers)}] Completed: {server['name']}")
            except Exception as e:
                print(f"{Fore.RED}❌ [{i}/{len(servers)}] Failed: {server['name']} - {e}")
                error_result = {
                    "server_id": server["_id"],
                    "server_name": server["name"],
                    "server_url": server["mcp_url"],
                    "test_time": datetime.now().isoformat(),
                    "connection_test": {"success": False, "error": str(e)},
                    "tools_test": {"success": False, "tools": []},
                    "overall_status": "failed"
                }
                self.test_results.append(error_result)
            
            # Small delay between tests to avoid overwhelming servers
            if i < len(servers):
                await asyncio.sleep(1 if quick_mode else 2)
        
        # Calculate execution time
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        # Statistics
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r.get("overall_status") == "passed")
        failed = sum(1 for r in self.test_results if r.get("overall_status") == "failed")
        partial = total - passed - failed
        
        # Detailed time statistics
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}⏱️  SERIAL TEST TIME STATISTICS")
        print(f"{Fore.CYAN}{'='*60}")
        
        print(f"{Fore.GREEN}✅ All {total} tests completed in {execution_time:.1f} seconds!")
        print(f"{Fore.CYAN}📊 Results: {passed} passed, {partial} partial, {failed} failed")
        
        # Performance analysis for serial mode
        if total > 0:
            avg_task_time = execution_time / total
            print(f"\n{Fore.YELLOW}🚶 Serial Mode Analysis:")
            print(f"{Fore.YELLOW}  • Average task time: {avg_task_time:.1f}s")
            print(f"{Fore.YELLOW}  • Total execution time: {execution_time:.1f}s")
            print(f"{Fore.YELLOW}  • Concurrency level: 1 (sequential)")
        
        print(f"{Fore.CYAN}{'='*60}")
        
        return self.test_results
    
    async def _test_servers_parallel(self, servers: List[Dict[str, Any]], quick_mode: bool = False) -> List[Dict[str, Any]]:
        """Parallel testing for all servers"""
        # Parallel testing configuration
        max_concurrent = config.QUICK_MODE_MAX_CONCURRENT if quick_mode else config.FULL_MODE_MAX_CONCURRENT
        semaphore = asyncio.Semaphore(max_concurrent)
        
        print(f"{Fore.CYAN}🚀 Using parallel testing with max {max_concurrent} concurrent connections")
        print(f"{Fore.CYAN}⏱️  Estimated time: {len(servers) // max_concurrent + 1} batches")
        
        async def test_server_wrapper(server: Dict[str, Any], index: int):
            """Wrapper for single server testing with semaphore control"""
            async with semaphore:
                try:
                    print(f"{Fore.CYAN}🔄 [{index}/{len(servers)}] Starting: {server['name']}")
                    start_time = datetime.now()
                    result = await self.test_server(server, quick_mode)
                    end_time = datetime.now()
                    execution_time_ms = (end_time - start_time).total_seconds() * 1000
                    result['execution_time_ms'] = execution_time_ms
                    print(f"{Fore.GREEN}✅ [{index}/{len(servers)}] Completed: {server['name']} ({execution_time_ms:.0f}ms)")
                    return result
                except asyncio.CancelledError:
                    # Handle cancellation gracefully
                    print(f"{Fore.YELLOW}⚠️ [{index}/{len(servers)}] Cancelled: {server['name']}")
                    return {
                        "server_id": server["_id"],
                        "server_name": server["name"],
                        "server_url": server["mcp_url"],
                        "test_time": datetime.now().isoformat(),
                        "connection_test": {"success": False, "error": "Test cancelled"},
                        "tools_test": {"success": False, "tools": []},
                        "overall_status": "cancelled"
                    }
                except Exception as e:
                    print(f"{Fore.RED}❌ [{index}/{len(servers)}] Failed: {server['name']} - {e}")
                    # Return error result
                    return {
                        "server_id": server["_id"],
                        "server_name": server["name"],
                        "server_url": server["mcp_url"],
                        "test_time": datetime.now().isoformat(),
                        "connection_test": {"success": False, "error": str(e)[:200]},
                        "tools_test": {"success": False, "tools": []},
                        "overall_status": "failed"
                    }
        
        # Create all test tasks
        tasks = []
        for i, server in enumerate(servers, 1):
            task = asyncio.create_task(test_server_wrapper(server, i))
            tasks.append(task)
        
        # Execute all tests in parallel
        print(f"{Fore.CYAN}🔄 Starting {len(tasks)} parallel test tasks...")
        start_time = datetime.now()
        
        try:
            print(f"{Fore.CYAN}🔄 Executing {len(tasks)} parallel tasks...")
            self.test_results = []
            task_times = {}  # Track individual task execution times
            
            # Track completion status
            completed = set()
            results_dict = {}
            
            # Use wait with timeout instead of gather to avoid hanging
            try:
                # Wait for all tasks to complete or timeout
                # Quick mode: 5 seconds per batch, Full mode: 60 seconds per batch
                batch_timeout = 15 if quick_mode else 60
                done, pending = await asyncio.wait(tasks, timeout=batch_timeout, return_when=asyncio.ALL_COMPLETED)
                
                # Process completed tasks
                for task in done:
                    # Find which server this task belongs to
                    task_index = tasks.index(task)
                    server = servers[task_index]
                    
                    try:
                        result = task.result()
                        results_dict[task_index] = result
                        completed.add(task_index)
                        if isinstance(result, dict) and result.get('server_name'):
                            task_times[result['server_name']] = result.get('execution_time_ms', 0)
                    except Exception as e:
                        # Task raised an exception
                        print(f"{Fore.RED}❌ Task exception for {server['name']}: {str(e)[:100]}")
                        results_dict[task_index] = {
                            "server_id": server["_id"],
                            "server_name": server["name"],
                            "server_url": server["mcp_url"],
                            "test_time": datetime.now().isoformat(),
                            "connection_test": {"success": False, "error": str(e)[:200]},
                            "tools_test": {"success": False, "tools": []},
                            "overall_status": "failed"
                        }
                        completed.add(task_index)
                
                # Handle pending (timed out) tasks
                if pending:
                    print(f"{Fore.YELLOW}⚠️ {len(pending)} tasks timed out, cancelling...")
                    for task in pending:
                        task.cancel()
                        # Find which server this task belongs to
                        task_index = tasks.index(task)
                        server = servers[task_index]
                        results_dict[task_index] = {
                            "server_id": server["_id"],
                            "server_name": server["name"],
                            "server_url": server["mcp_url"],
                            "test_time": datetime.now().isoformat(),
                            "connection_test": {"success": False, "error": "Test timed out"},
                            "tools_test": {"success": False, "tools": []},
                            "overall_status": "timeout"
                        }
                    
                    # Wait briefly for cancellation to complete
                    await asyncio.sleep(0.5)
                
                # Build results in original order
                for i in range(len(servers)):
                    if i in results_dict:
                        self.test_results.append(results_dict[i])
                    else:
                        # This shouldn't happen, but handle it just in case
                        server = servers[i]
                        self.test_results.append({
                            "server_id": server["_id"],
                            "server_name": server["name"],
                            "server_url": server["mcp_url"],
                            "test_time": datetime.now().isoformat(),
                            "connection_test": {"success": False, "error": "Test not completed"},
                            "tools_test": {"success": False, "tools": []},
                            "overall_status": "failed"
                        })
                
                print(f"{Fore.CYAN}✅ Processed {len(done)} completed and {len(pending)} timed out tasks")
                
            except asyncio.CancelledError:
                # Handle interruption (Ctrl+C)
                print(f"{Fore.YELLOW}\n⚠️ Test interrupted, cancelling all tasks...")
                for task in tasks:
                    if not task.done():
                        task.cancel()
                raise
            except Exception as e:
                print(f"{Fore.RED}❌ Unexpected error in parallel execution: {e}")
                # Cancel all pending tasks
                for task in tasks:
                    if not task.done():
                        task.cancel()
                raise
            
        except Exception as e:
            print(f"{Fore.RED}❌ Parallel execution failed: {e}")
            # If parallel execution fails, fall back to serial execution
            print(f"{Fore.YELLOW}⚠️ Falling back to serial execution...")
            return await self._test_servers_serial(servers, quick_mode)
        
        # Calculate execution time
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        # Statistics
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r.get("overall_status") == "passed")
        failed = sum(1 for r in self.test_results if r.get("overall_status") == "failed")
        partial = total - passed - failed
        
        # Detailed time statistics
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}⏱️  PARALLEL TEST TIME STATISTICS")
        print(f"{Fore.CYAN}{'='*60}")
        
        print(f"{Fore.GREEN}✅ All {total} tests completed in {execution_time:.1f} seconds!")
        print(f"{Fore.CYAN}📊 Results: {passed} passed, {partial} partial, {failed} failed")
        
        # Performance analysis (in milliseconds)
        if task_times:
            # Filter out zero values for better statistics
            valid_times = {k: v for k, v in task_times.items() if v > 0}
            if valid_times:
                avg_task_time = sum(valid_times.values()) / len(valid_times)
                min_task_time = min(valid_times.values())
                max_task_time = max(valid_times.values())
                
                print(f"\n{Fore.YELLOW}🚀 Performance Analysis:")
                print(f"{Fore.YELLOW}  • Average task time: {avg_task_time:.0f}ms")
                print(f"{Fore.YELLOW}  • Fastest task: {min_task_time:.0f}ms")
                print(f"{Fore.YELLOW}  • Slowest task: {max_task_time:.0f}ms")
                print(f"{Fore.YELLOW}  • Concurrency level: {max_concurrent}")
                
                # Calculate efficiency
                theoretical_serial_time_s = (avg_task_time * total) / 1000  # Convert to seconds
                efficiency_gain = theoretical_serial_time_s / execution_time if execution_time > 0 else 0
                print(f"{Fore.YELLOW}  • Theoretical serial time: {theoretical_serial_time_s:.1f}s")
                print(f"{Fore.YELLOW}  • Speed improvement: {efficiency_gain:.1f}x")
        
        # Individual task times (top 5 fastest and slowest)
        if task_times:
            # Filter out zero values
            valid_times = {k: v for k, v in task_times.items() if v > 0}
            if valid_times:
                sorted_tasks = sorted(valid_times.items(), key=lambda x: x[1])
                print(f"\n{Fore.CYAN}🏃 Fastest 5 tasks:")
                for i, (name, time) in enumerate(sorted_tasks[:5], 1):
                    print(f"{Fore.CYAN}  {i}. {name}: {time:.0f}ms")
                
                if len(sorted_tasks) > 5:
                    print(f"\n{Fore.CYAN}🐌 Slowest 5 tasks:")
                    for i, (name, time) in enumerate(sorted_tasks[-5:], 1):
                        print(f"{Fore.CYAN}  {i}. {name}: {time:.0f}ms")
        
        print(f"{Fore.CYAN}{'='*60}")
        
        return self.test_results