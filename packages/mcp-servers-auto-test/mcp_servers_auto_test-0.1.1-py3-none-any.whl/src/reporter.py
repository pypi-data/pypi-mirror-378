import json
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path
from tabulate import tabulate
from colorama import Fore, Style, init

init(autoreset=True)


class TestReporter:
    def __init__(self, output_dir: str = "test_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def save_results(self, results: List[Dict[str, Any]], filename: str = None) -> str:
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"mcp_test_results_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n{Fore.GREEN}📁 Results saved to: {filepath}")
        return str(filepath)
    
    def generate_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        total_servers = len(results)
        passed = sum(1 for r in results if r["overall_status"] == "passed")
        partial = sum(1 for r in results if r["overall_status"] == "partial")
        failed = sum(1 for r in results if r["overall_status"] == "failed")
        
        connection_success = sum(1 for r in results if r["connection_test"]["success"])
        tools_success = sum(1 for r in results if r["tools_test"]["success"])
        
        summary = {
            "test_time": datetime.now().isoformat(),
            "total_servers": total_servers,
            "passed": passed,
            "partial": partial,
            "failed": failed,
            "success_rate": (passed / total_servers * 100) if total_servers > 0 else 0,
            "connection_success_rate": (connection_success / total_servers * 100) if total_servers > 0 else 0,
            "tools_success_rate": (tools_success / total_servers * 100) if total_servers > 0 else 0
        }
        
        return summary
    
    def print_report(self, results: List[Dict[str, Any]]):
        print(f"\n{Fore.MAGENTA}{'='*80}")
        print(f"{Fore.MAGENTA}{'MCP SERVERS AUTOMATED TEST REPORT':^80}")
        print(f"{Fore.MAGENTA}{'='*80}\n")
        
        # Summary statistics
        summary = self.generate_summary(results)
        
        print(f"{Fore.CYAN}Test Summary:")
        print(f"  Total Servers Tested: {summary['total_servers']}")
        print(f"  {Fore.GREEN}Passed: {summary['passed']} ({summary['passed']/summary['total_servers']*100:.1f}%)")
        print(f"  {Fore.YELLOW}Partial: {summary['partial']} ({summary['partial']/summary['total_servers']*100:.1f}%)")
        print(f"  {Fore.RED}Failed: {summary['failed']} ({summary['failed']/summary['total_servers']*100:.1f}%)")
        print(f"\n  Connection Success Rate: {summary['connection_success_rate']:.1f}%")
        print(f"  Tools Test Success Rate: {summary['tools_success_rate']:.1f}%")
        
        # Detailed results table
        print(f"\n{Fore.CYAN}Detailed Results:")
        print(f"{Fore.CYAN}{'-'*80}")
        
        table_data = []
        for result in results:
            status_icon = {
                "passed": "✅",
                "partial": "⚠️",
                "failed": "❌"
            }.get(result["overall_status"], "❓")
            
            connection_status = "✅" if result["connection_test"]["success"] else "❌"
            tools_count = result["tools_test"].get("total_tools", 0)
            tools_rate = result["tools_test"].get("success_rate", 0)
            tools_status = f"{tools_count} tools ({tools_rate:.0%})" if result["tools_test"]["success"] else "❌"
            
            table_data.append([
                result["server_name"][:30],
                connection_status,
                tools_status,
                f"{status_icon} {result['overall_status'].upper()}"
            ])
        
        headers = ["Server Name", "Connection", "Tools", "Status"]
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        
        # Failed servers details
        failed_servers = [r for r in results if r["overall_status"] == "failed"]
        if failed_servers:
            print(f"\n{Fore.RED}Failed Servers Details:")
            print(f"{Fore.RED}{'-'*80}")
            for server in failed_servers:
                print(f"\n  {server['server_name']}:")
                print(f"    URL: {server['server_url']}")
                if not server["connection_test"]["success"]:
                    error = server["connection_test"].get("error", "Unknown error")
                    print(f"    Connection Error: {error}")
                if not server["tools_test"]["success"]:
                    error = server["tools_test"].get("error", "Unknown error")
                    print(f"    Tools Error: {error}")
        
        print(f"\n{Fore.MAGENTA}{'='*80}\n")
    
    def generate_html_report(self, results: List[Dict[str, Any]]) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"mcp_test_report_{timestamp}.html"
        filepath = self.output_dir / filename
        
        summary = self.generate_summary(results)
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>MCP Servers Test Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                .summary {{ background: #f0f0f0; padding: 15px; margin: 20px 0; border-radius: 5px; }}
                .passed {{ color: green; }}
                .partial {{ color: orange; }}
                .failed {{ color: red; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #4CAF50; color: white; }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>MCP Servers Automated Test Report</h1>
            <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            
            <div class="summary">
                <h2>Summary</h2>
                <p>Total Servers: {summary['total_servers']}</p>
                <p class="passed">Passed: {summary['passed']} ({summary['success_rate']:.1f}%)</p>
                <p class="partial">Partial: {summary['partial']}</p>
                <p class="failed">Failed: {summary['failed']}</p>
                <p>Connection Success Rate: {summary['connection_success_rate']:.1f}%</p>
                <p>Tools Test Success Rate: {summary['tools_success_rate']:.1f}%</p>
            </div>
            
            <h2>Detailed Results</h2>
            <table>
                <tr>
                    <th>Server Name</th>
                    <th>URL</th>
                    <th>Connection</th>
                    <th>Tools</th>
                    <th>Status</th>
                </tr>
        """
        
        for result in results:
            status_class = result["overall_status"]
            connection = "✅" if result["connection_test"]["success"] else "❌"
            tools_count = result["tools_test"].get("total_tools", 0)
            tools_rate = result["tools_test"].get("success_rate", 0)
            tools = f"{tools_count} ({tools_rate:.0%})" if result["tools_test"]["success"] else "❌"
            
            html_content += f"""
                <tr>
                    <td>{result['server_name']}</td>
                    <td>{result['server_url']}</td>
                    <td>{connection}</td>
                    <td>{tools}</td>
                    <td class="{status_class}">{result['overall_status'].upper()}</td>
                </tr>
            """
        
        html_content += """
            </table>
        </body>
        </html>
        """
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print(f"{Fore.GREEN}📄 HTML report saved to: {filepath}")
        return str(filepath)