import asyncio
import json
from typing import Optional, List, Dict, Any
from datetime import timedelta
from mcp import ClientSession
from mcp.client.sse import sse_client
from openai import OpenAI
from src.config import config


class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self._session_context = None
        self._streams_context = None
        self.openai = OpenAI(api_key=config.OPENAI_API_KEY) if config.OPENAI_API_KEY else None
        
    async def connect(self, server_url: str, transport: str = "sse") -> bool:
        try:
            if transport == "streamable_http":
                await self._connect_streamable_http(server_url)
            else:
                await self._connect_sse(server_url)
            return True
        except BaseException as e:
            # Catch all exceptions including BaseExceptionGroup
            error_msg = str(e)
            if "BaseExceptionGroup" in str(type(e).__name__):
                # Extract more meaningful error from BaseExceptionGroup
                if "403 Forbidden" in error_msg:
                    error_msg = "403 Forbidden - Access denied (check API key)"
                elif "404" in error_msg:
                    error_msg = "404 Not Found - Server endpoint not available"
                elif "timeout" in error_msg.lower():
                    error_msg = "Connection timeout"
                elif "Not Acceptable" in error_msg:
                    error_msg = "406 Not Acceptable - Client must accept text/event-stream"
                else:
                    error_msg = f"Connection error: {error_msg[:100]}"
            print(f"❌ Connection failed for {server_url}: {error_msg}")
            await self.cleanup()
            return False
    
    async def _connect_streamable_http(self, server_url: str):
        try:
            from mcp.client.streamable_http import streamablehttp_client
            
            self._streams_context = streamablehttp_client(
                url=server_url,
                timeout=config.DEFAULT_TIMEOUT,
                sse_read_timeout=config.SSE_READ_TIMEOUT
            )
            streams = await self._streams_context.__aenter__()
            
            read_stream, write_stream, get_session_id = streams
            self._session_context = ClientSession(
                read_stream,
                write_stream,
                read_timeout_seconds=timedelta(seconds=config.SSE_READ_TIMEOUT)
            )
            self.session = await self._session_context.__aenter__()
            await self.session.initialize()
        except BaseException as e:
            await self.cleanup()
            raise
        
    async def _connect_sse(self, server_url: str):
        try:
            self._streams_context = sse_client(url=server_url)
            streams = await self._streams_context.__aenter__()
            
            self._session_context = ClientSession(*streams)
            self.session = await self._session_context.__aenter__()
            await self.session.initialize()
        except BaseException as e:
            await self.cleanup()
            raise
    
    async def get_tools(self) -> List[Dict[str, Any]]:
        if not self.session:
            raise ValueError("Client not connected")
        
        try:
            response = await self.session.list_tools()
            tools = [{
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
            } for tool in response.tools]
            
            return tools
        except Exception as e:
            print(f"Failed to get tools: {e}")
            return []
    
    async def test_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
        if not self.session:
            raise ValueError("Client not connected")
        
        try:
            result = await self.session.call_tool(tool_name, tool_args)
            result_content = result.content if hasattr(result, 'content') else str(result)
            
            # Analyze the result semantically
            semantic_analysis = await self.analyze_tool_result(result_content)
            
            return {
                "success": True if semantic_analysis["status"] == "success" else False,
                "result": result_content,
                "semantic_analysis": semantic_analysis
            }
        
        except Exception as e:
            print(f"Failed to test tool: {e}")
            return {
                "success": False,
                "error": str(e),
                "semantic_analysis": {
                    "status": "error",
                    "issue_type": "exception",
                    "message": str(e)
                }
            }
        except BaseException as e:
            # Handle all types of exceptions including validation errors
            error_str = str(e)
            
            # Check for specific error patterns
            if "ValidationError" in str(type(e).__name__) or "validation error" in error_str.lower():
                error_msg = "Server response validation error - incompatible response format"
            elif "SSE message" in error_str:
                error_msg = "SSE message parsing error - server may return invalid format"
            elif len(error_str) > 200:
                error_msg = error_str[:200] + "..."
            else:
                error_msg = error_str
            
            return {
                "success": False,
                "error": error_msg,
                "semantic_analysis": {
                    "status": "error",
                    "issue_type": "validation" if "validation" in error_str.lower() else "exception",
                    "message": error_msg
                }
            }
    
    async def generate_tool_test_params(self, tool: Dict[str, Any]) -> Dict[str, Any]:
        if not self.openai:
            return {}
        
        tool_function = tool["function"]
        
        # Handle tools with no parameters or empty parameter schemas
        params_schema = tool_function.get('parameters', {})
        if not params_schema or params_schema == {} or params_schema.get('properties', {}) == {}:
            # Tool has no parameters, return empty dict
            return {}
        
        # Get current date for context
        from datetime import datetime, timedelta
        today = datetime.now()
        tomorrow = today + timedelta(days=1)
        next_week = today + timedelta(days=7)
        next_month = today + timedelta(days=30)
        
        # Create more detailed prompt with examples based on tool name
        tool_name = tool_function['name'].lower()
        tool_desc = tool_function.get('description', '')
        
        # Add context-specific hints based on common tool patterns
        context_hints = ""
        if any(word in tool_name for word in ['flight', 'airport', 'airline']):
            context_hints = f"""
            For flight/airport related fields:
            - Use real airport codes like: PEK (Beijing), SHA (Shanghai), CAN (Guangzhou), SZX (Shenzhen)
            - Use real airline codes like: CA (Air China), MU (China Eastern), CZ (China Southern)
            - Use dates between {tomorrow.strftime('%Y-%m-%d')} and {next_month.strftime('%Y-%m-%d')}
            - Flight numbers like: CA1234, MU5678
            - Example date: {next_week.strftime('%Y-%m-%d')}
            """
        elif any(word in tool_name for word in ['train', 'station', 'railway', '12306']):
            context_hints = f"""
            For train/railway related fields:
            - Use real Chinese city names: 北京, 上海, 广州, 深圳, 杭州
            - Use real station codes if needed: BJP (Beijing), SHH (Shanghai), GZQ (Guangzhou)
            - Use dates between {tomorrow.strftime('%Y-%m-%d')} and {next_month.strftime('%Y-%m-%d')}
            - Train numbers like: G1234, D5678, K9012
            - Example date: {next_week.strftime('%Y-%m-%d')}
            """
        elif any(word in tool_name for word in ['map', 'location', 'geocode', 'address']):
            context_hints = """
            For location/map related fields:
            - Use real coordinates: latitude 39.9042 (Beijing), longitude 116.4074
            - Use real addresses: 北京市朝阳区建国门外大街1号
            - Use real city names: Beijing, Shanghai, New York, London
            - Distance in meters: 1000, 5000, 10000
            """
        elif any(word in tool_name for word in ['weather', 'temperature', 'forecast']):
            context_hints = """
            For weather related fields:
            - Use real city names: Beijing, Shanghai, New York, London
            - Use valid date formats: 2024-12-25, today, tomorrow
            - Temperature units: celsius, fahrenheit
            """
        elif any(word in tool_name for word in ['search', 'query', 'find']):
            context_hints = """
            For search related fields:
            - Use realistic search queries: "machine learning", "climate change", "Python programming"
            - Use reasonable result limits: 10, 20, 50
            - Use real language codes: en, zh, fr, de
            """
        elif any(word in tool_name for word in ['file', 'path', 'directory']):
            context_hints = """
            For file/path related fields:
            - Use realistic file paths: /home/user/documents/report.pdf, ./data/config.json
            - Use common file names: README.md, config.yaml, data.csv
            - Use realistic content: "Hello World", "Test content", "Sample data"
            """
        elif 'date' in tool_name or 'time' in tool_name:
            context_hints = """
            For date/time related fields:
            - Use ISO format: 2024-12-25, 2024-12-25T10:30:00
            - Use relative dates: today, tomorrow, yesterday
            - Use realistic time ranges: last_week, next_month
            """
        
        prompt = f"""
        Generate realistic test parameters for this API tool.
        
        CURRENT DATE CONTEXT:
        - Today is: {today.strftime('%Y-%m-%d')}
        - Tomorrow: {tomorrow.strftime('%Y-%m-%d')}
        - Next week: {next_week.strftime('%Y-%m-%d')}
        - Next month: {next_month.strftime('%Y-%m-%d')}
        
        Tool Name: {tool_function['name']}
        Description: {tool_desc}
        
        Parameters Schema:
        {json.dumps(params_schema, indent=2)}
        
        {context_hints}
        
        IMPORTANT RULES:
        1. Generate REALISTIC values that would work in a real scenario
        2. For required fields, ALWAYS provide a value
        3. For optional fields, include them if they make the test more comprehensive
        4. Use real-world data (real city names, valid codes, actual dates, etc.)
        5. For arrays, provide 1-3 example items
        6. For numbers, use reasonable ranges (not 0 or 1, but realistic values)
        7. For dates, MUST use FUTURE dates between tomorrow ({tomorrow.strftime('%Y-%m-%d')}) and next month ({next_month.strftime('%Y-%m-%d')})
        8. For strings, use meaningful text, not "test" or "example"
        9. NEVER use past dates or today's date for future events (flights, trains, etc.)
        
        Examples of good test values:
        - City: "Beijing", "上海", "New York"  
        - Date: "{next_week.strftime('%Y-%m-%d')}", "{(today + timedelta(days=10)).strftime('%Y-%m-%d')}"
        - Query: "artificial intelligence news", "Python tutorial"
        - Number: 42, 100, 2024
        - Boolean: true or false (based on what makes sense)
        
        Return ONLY a valid JSON object with the test parameters.
        Do NOT include any explanation or markdown formatting.
        """
        
        try:
            response = self.openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert API test data generator. You understand various API parameter requirements and generate realistic, valid test data. Always return pure JSON without any markdown formatting or explanations. When you see Chinese tool names or descriptions, generate appropriate Chinese test data."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,  # Slightly higher for more variety
                max_tokens=800  # More tokens for complex parameters
            )
            
            content = response.choices[0].message.content
            if not content or content.strip() == "":
                print(f"⚠️ Empty response from OpenAI for {tool_function['name']}")
                return {}
                
            # Clean the content (remove markdown code blocks if present)
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            return json.loads(content)
        except json.JSONDecodeError as e:
            print(f"⚠️ Failed to parse JSON for {tool_function['name']}: {e}")
            print(f"   Response content: {content[:200] if 'content' in locals() else 'No content'}")
            return {}
        except Exception as e:
            error_str = str(e)
            if "rate_limit" in error_str.lower() or "429" in error_str:
                print(f"⚠️ Rate limit hit for {tool_function['name']}, waiting 2 seconds...")
                import time
                time.sleep(2)  # Simple rate limit handling
            elif "insufficient_quota" in error_str.lower() or "quota" in error_str.lower():
                print(f"⚠️ OpenAI quota issue for {tool_function['name']}: {e}")
            else:
                print(f"⚠️ Failed to generate test params for {tool_function['name']}: {e}")
            return {}
    
    async def analyze_tool_result(self, result_content: str) -> Dict[str, Any]:
        """Analyze tool result semantically to detect API key issues or other problems"""
        if not self.openai:
            # Simple keyword-based analysis if no OpenAI available
            result_lower = str(result_content).lower()
            
            # Check for API key issues
            if any(keyword in result_lower for keyword in [
                'api key', 'apikey', 'api_key', 'authentication', 'unauthorized',
                'invalid key', 'missing key', 'no key', 'key required', 'api-key',
                'please provide', 'please set', 'not configured', 'not found key'
            ]):
                return {
                    "status": "api_key_missing",
                    "issue_type": "configuration",
                    "message": "API key appears to be missing or invalid"
                }
            
            # Check for quota/billing issues
            if any(keyword in result_lower for keyword in [
                'quota', 'exceeded', 'limit', 'billing', 'payment', 'credit',
                'insufficient', 'expired', 'suspended', 'rate limit', 'too many requests',
                'overdue', 'unpaid', 'balance', 'fund'
            ]):
                return {
                    "status": "quota_exceeded",
                    "issue_type": "billing",
                    "message": "API quota exceeded or billing issue"
                }
            
            # Check for error indicators
            if any(keyword in result_lower for keyword in [
                'error', 'failed', 'exception', 'cannot', 'unable', 'invalid'
            ]):
                return {
                    "status": "error",
                    "issue_type": "general",
                    "message": "Tool returned an error"
                }
            
            return {
                "status": "success",
                "issue_type": None,
                "message": "Tool executed successfully"
            }
        
        # Use LLM for semantic analysis
        try:
            prompt = f"""
            Analyze the following API response and determine if there are any issues.
            
            Response to analyze:
            {result_content[:1000]}  # Limit to first 1000 chars
            
            Check for:
            1. API key missing or invalid
            2. Quota exceeded or billing issues
            3. General errors
            
            Return ONLY a JSON object with this structure:
            {{
                "status": "success" | "api_key_missing" | "quota_exceeded" | "error",
                "issue_type": "configuration" | "billing" | "general" | null,
                "message": "Brief description of the issue or 'Tool executed successfully'"
            }}
            """
            
            response = self.openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an API response analyzer. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=200
            )
            
            content = response.choices[0].message.content
            analysis = json.loads(content)
            return analysis
            
        except Exception as e:
            # Fallback to keyword analysis if LLM fails
            result_lower = str(result_content).lower()
            if 'api' in result_lower and 'key' in result_lower:
                return {
                    "status": "api_key_missing",
                    "issue_type": "configuration",
                    "message": "Possible API key issue detected"
                }
            return {
                "status": "success",
                "issue_type": None,
                "message": "Tool executed (analysis unavailable)"
            }
    
    async def cleanup(self):
        """Clean up connections, suppressing all errors"""
        import warnings
        import sys
        
        # Temporarily suppress stderr to avoid cleanup error messages
        original_stderr = sys.stderr
        try:
            # Redirect stderr to null during cleanup
            import os
            sys.stderr = open(os.devnull, 'w')
            
            # Clean up session first
            if self._session_context:
                try:
                    await self._session_context.__aexit__(None, None, None)
                except (BaseException, GeneratorExit):
                    pass
                finally:
                    self._session_context = None
            
            # Then clean up streams
            if self._streams_context:
                try:
                    await self._streams_context.__aexit__(None, None, None)
                except (BaseException, GeneratorExit):
                    pass
                finally:
                    self._streams_context = None
                    
            # Reset session
            self.session = None
        except BaseException:
            # Ignore all cleanup errors
            pass
        finally:
            # Restore stderr
            sys.stderr = original_stderr