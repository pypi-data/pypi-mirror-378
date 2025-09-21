import asyncio
import signal
import sys
from datetime import datetime, time, timedelta
from pathlib import Path
from typing import List, Dict, Any
from colorama import Fore, Style, init

init(autoreset=True)


class TestScheduler:
    def __init__(self, quick_interval_minutes: int = 30, test_mode: str = "parallel"):
        self.quick_interval_seconds = quick_interval_minutes * 60
        self.running = False
        self.md_report_file = Path("test_results/test_report.md")
        self.md_report_file.parent.mkdir(exist_ok=True)
        self.test_mode = test_mode
        
        # Full test times: 8:00, 12:00, 16:00, 20:00
        self.full_test_hours = [8, 12, 16, 20]
        
        # Initialize MD file if it doesn't exist
        if not self.md_report_file.exists():
            with open(self.md_report_file, "w", encoding="utf-8") as f:
                f.write("# MCP Servers Automated Test Report\n\n")
                f.write("This file contains the cumulative test results for MCP servers.\n\n")
                f.write("---\n\n")
    
    def should_run_full_test(self) -> bool:
        """Check if current time is a full test time"""
        now = datetime.now()
        current_hour = now.hour
        current_minute = now.minute
        
        # Run full test if within 5 minutes of scheduled time
        for hour in self.full_test_hours:
            if current_hour == hour and current_minute < 5:
                return True
        return False
    
    def get_next_full_test_time(self) -> datetime:
        """Calculate when the next full test should run"""
        now = datetime.now()
        today = now.date()
        
        # Find next scheduled time today
        for hour in self.full_test_hours:
            test_time = datetime.combine(today, time(hour, 0))
            if test_time > now:
                return test_time
        
        # If no more tests today, return first test tomorrow
        tomorrow = datetime.combine(today, time(self.full_test_hours[0], 0))
        return tomorrow + timedelta(days=1)
    
    def append_to_md_report(self, results: List[Dict[str, Any]], test_mode: str = "QUICK"):
        """Append test results to the markdown report file"""
        with open(self.md_report_file, "a", encoding="utf-8") as f:
            # Write test session header
            f.write(f"## Test Session: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [{test_mode} MODE]\n\n")
            
            # Summary statistics
            total = len(results)
            passed = sum(1 for r in results if r["overall_status"] == "passed")
            partial = sum(1 for r in results if r["overall_status"] == "partial")
            failed = sum(1 for r in results if r["overall_status"] == "failed")
            
            f.write("### Summary\n\n")
            f.write(f"- **Test Mode:** {test_mode}\n")
            f.write(f"- **Total Servers Tested:** {total}\n")
            f.write(f"- **Passed:** {passed} ({passed/total*100:.1f}%)\n")
            f.write(f"- **Partial:** {partial} ({partial/total*100:.1f}%)\n")
            f.write(f"- **Failed:** {failed} ({failed/total*100:.1f}%)\n\n")
            
            # Results table
            f.write("### Detailed Results\n\n")
            f.write("| Server Name | URL | Connection | Tools | Status | Failure Reason |\n")
            f.write("|-------------|-----|------------|-------|--------|----------------|\n")
            
            for result in results:
                name = result["server_name"][:30]
                url = result["server_url"][:40] + "..." if len(result["server_url"]) > 40 else result["server_url"]
                
                connection = "✅" if result["connection_test"]["success"] else "❌"
                
                if result["tools_test"]["success"]:
                    tools_count = result["tools_test"].get("total_tools", 0)
                    tools_rate = result["tools_test"].get("success_rate", 0)
                    tools = f"{tools_count} ({tools_rate:.0%})"
                else:
                    tools = "❌"
                
                status_icon = {
                    "passed": "✅ PASSED",
                    "partial": "⚠️ PARTIAL",
                    "failed": "❌ FAILED"
                }.get(result["overall_status"], "❓ UNKNOWN")
                
                # Collect failure reasons
                failure_reasons = []
                if not result["connection_test"]["success"]:
                    error = result["connection_test"].get("error", "Connection failed")
                    failure_reasons.append(f"Connection: {error[:50]}")
                if not result["tools_test"]["success"] and "error" in result["tools_test"]:
                    error = result["tools_test"].get("error", "Tools test failed")
                    failure_reasons.append(f"Tools: {error[:50]}")
                
                # Check for API issues
                api_issues = []
                for tool in result["tools_test"].get("tools", []):
                    if tool.get("api_issue") == "api_key_missing":
                        api_issues.append("API Key Missing")
                        break
                    elif tool.get("api_issue") == "quota_exceeded":
                        api_issues.append("Quota Exceeded")
                        break
                
                if api_issues:
                    failure_reasons.extend(api_issues)
                
                failure_reason = " / ".join(failure_reasons) if failure_reasons else "N/A"
                
                f.write(f"| {name} | {url} | {connection} | {tools} | {status_icon} | {failure_reason} |\n")
            
            # Failed servers details (only for full tests)
            if test_mode == "FULL":
                failed_servers = [r for r in results if r["overall_status"] == "failed"]
                if failed_servers:
                    f.write("\n### Failed Servers Details\n\n")
                    for server in failed_servers:
                        f.write(f"#### {server['server_name']}\n\n")
                        f.write(f"- **URL:** {server['server_url']}\n")
                        f.write(f"- **Test Time:** {server['test_time']}\n")
                        
                        if not server["connection_test"]["success"]:
                            error = server["connection_test"].get("error", "Unknown error")
                            f.write(f"- **Connection Error:** {error}\n")
                        
                        if not server["tools_test"]["success"] and "error" in server["tools_test"]:
                            error = server["tools_test"].get("error", "Unknown error")
                            f.write(f"- **Tools Error:** {error}\n")
                        
                        f.write("\n")
            
            f.write("\n---\n\n")
        
        print(f"{Fore.GREEN}📝 Results appended to: {self.md_report_file}")
    
    def print_screen_report(self, results: List[Dict[str, Any]], test_mode: str = "QUICK"):
        """Print formatted test results to screen"""
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.CYAN}{'TEST RESULTS':^80}")
        print(f"{Fore.CYAN}{f'[{test_mode} MODE]':^80}")
        print(f"{Fore.CYAN}{datetime.now().strftime('%Y-%m-%d %H:%M:%S'):^80}")
        print(f"{Fore.CYAN}{'='*80}\n")
        
        # Summary
        total = len(results)
        passed = sum(1 for r in results if r["overall_status"] == "passed")
        partial = sum(1 for r in results if r["overall_status"] == "partial")
        failed = sum(1 for r in results if r["overall_status"] == "failed")
        
        print(f"{Fore.WHITE}Summary:")
        print(f"  Mode: {test_mode} | Total: {total} | {Fore.GREEN}Passed: {passed}{Fore.WHITE} | {Fore.YELLOW}Partial: {partial}{Fore.WHITE} | {Fore.RED}Failed: {failed}{Fore.WHITE}\n")
        
        # Results list (compact for quick mode, detailed for full mode)
        print(f"{Fore.WHITE}Results:")
        print(f"{'-'*80}")
        
        if test_mode == "QUICK":
            # Compact display for quick mode
            for i, result in enumerate(results, 1):
                status_color = {
                    "passed": Fore.GREEN,
                    "partial": Fore.YELLOW,
                    "failed": Fore.RED
                }.get(result["overall_status"], Fore.WHITE)
                
                status_icon = {
                    "passed": "✅",
                    "partial": "⚠️",
                    "failed": "❌"
                }.get(result["overall_status"], "❓")
                
                name = result['server_name'][:40].ljust(40)
                print(f"{i:3}. {name} {status_color}{status_icon} {result['overall_status'].upper()}{Style.RESET_ALL}")
                
                if result["overall_status"] == "failed":
                    if not result["connection_test"]["success"]:
                        error = result["connection_test"].get("error", "Connection failed")[:60]
                        print(f"     {Fore.RED}└─ {error}{Style.RESET_ALL}")
        else:
            # Detailed display for full mode
            for i, result in enumerate(results, 1):
                status_color = {
                    "passed": Fore.GREEN,
                    "partial": Fore.YELLOW,
                    "failed": Fore.RED
                }.get(result["overall_status"], Fore.WHITE)
                
                status_icon = {
                    "passed": "✅",
                    "partial": "⚠️",
                    "failed": "❌"
                }.get(result["overall_status"], "❓")
                
                print(f"\n{i}. {result['server_name']}")
                print(f"   URL: {result['server_url']}")
                print(f"   Status: {status_color}{status_icon} {result['overall_status'].upper()}{Style.RESET_ALL}")
                
                if result["overall_status"] == "failed":
                    print(f"   {Fore.RED}Failure Reasons:{Style.RESET_ALL}")
                    
                    if not result["connection_test"]["success"]:
                        error = result["connection_test"].get("error", "Connection failed")
                        print(f"     - Connection: {error}")
                    
                    if not result["tools_test"]["success"] and "error" in result["tools_test"]:
                        error = result["tools_test"].get("error", "Tools test failed")
                        print(f"     - Tools: {error}")
                
                elif result["overall_status"] == "passed":
                    tools_count = result["tools_test"].get("total_tools", 0)
                    print(f"   {Fore.GREEN}✓ Connection OK, {tools_count} tools available{Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}{'='*80}\n")
    
    async def run_test_cycle(self, quick_mode: bool = True):
        """Run a single test cycle"""
        from src.database import DatabaseManager
        from src.tester import ServerTester
        
        test_mode = "QUICK" if quick_mode else "FULL"
        print(f"\n{Fore.MAGENTA}🚀 Starting {test_mode} test cycle at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}...")
        
        db = DatabaseManager()
        tester = ServerTester()
        
        try:
            # Get servers from database
            await db.connect()
            servers = await db.get_hosted_servers()
            
            if not servers:
                print(f"{Fore.YELLOW}⚠️ No hosted servers found in database")
                return
            
            # Run tests
            results = await tester.test_all_servers(servers, quick_mode, self.test_mode)
            
            # Output results
            self.print_screen_report(results, test_mode)
            self.append_to_md_report(results, test_mode)
            
            # Update database with results (only for full tests)
            if not quick_mode:
                for result in results:
                    await db.update_server_test_result(result["server_id"], result)
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error during test cycle: {e}")
        finally:
            await db.close()
    
    async def start(self):
        """Start the scheduled testing with mixed frequencies"""
        self.running = True
        
        print(f"{Fore.MAGENTA}🔄 Test scheduler started")
        print(f"{Fore.MAGENTA}   Quick tests: Every {self.quick_interval_seconds // 60} minutes")
        print(f"{Fore.MAGENTA}   Full tests: At {', '.join(f'{h:02d}:00' for h in self.full_test_hours)}")
        print(f"{Fore.MAGENTA}   MD Report: {self.md_report_file}")
        print(f"{Fore.YELLOW}   Press Ctrl+C to stop\n")
        
        # Setup signal handlers
        def signal_handler(sig, frame):
            print(f"\n{Fore.YELLOW}⚠️ Stopping scheduler...")
            self.running = False
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        last_full_test_hour = -1
        
        while self.running:
            try:
                now = datetime.now()
                
                # Check if it's time for a full test
                if self.should_run_full_test() and now.hour != last_full_test_hour:
                    # Run full test
                    await self.run_test_cycle(quick_mode=False)
                    last_full_test_hour = now.hour
                else:
                    # Run quick test
                    await self.run_test_cycle(quick_mode=True)
                
                # Calculate next run time
                next_quick_time = datetime.now() + timedelta(seconds=self.quick_interval_seconds)
                next_full_time = self.get_next_full_test_time()
                
                print(f"\n{Fore.CYAN}💤 Next quick test at: {next_quick_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"{Fore.CYAN}   Next full test at: {next_full_time.strftime('%Y-%m-%d %H:%M:%S')}")
                
                await asyncio.sleep(self.quick_interval_seconds)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"{Fore.RED}❌ Scheduler error: {e}")
                print(f"{Fore.YELLOW}⚠️ Retrying in 60 seconds...")
                await asyncio.sleep(60)


