"""
Run Tool - Simplified command execution for AI agents.

Features:
- Single run_command() function with interactive flag
- Non-interactive: Auto-kill on timeout, return results
- Interactive: Stream output, agent controls with signals
- Enforces single command execution limit
"""

import os
import subprocess
import time
from typing import Dict, Any, Optional
from datetime import datetime


class RunTool:
    """Simplified command execution tool optimized for AI agents."""

    def __init__(self):
        self.active_process: Optional[Dict] = None  # Only one command at a time
        self.default_timeout = 300

    def run_command(
        self,
        command: str,
        timeout: int = 300,
        interactive: bool = False
    ) -> Dict[str, Any]:
        """
        Execute a command with simplified interface.

        Args:
            command: Command to execute
            timeout: Maximum execution time in seconds (default: 300)
            interactive: If True, stream output and agent controls; if False, auto-kill on timeout

        Returns:
            Dict with execution results or interactive process info
        """
        # Check if another command is already running
        if self.active_process is not None:
            return {
                "success": False,
                "error": "Another command is already running",
                "active_command": self.active_process.get("command", "unknown"),
                "suggestions": [
                    "Stop the current process first using stop_process()",
                    "Wait for the current command to complete",
                    "Use get_output() to check current command status"
                ]
            }

        if interactive:
            return self._run_interactive(command, timeout)
        else:
            return self._run_non_interactive(command, timeout)

    def _run_non_interactive(self, command: str, timeout: int) -> Dict[str, Any]:
        """Execute command in non-interactive mode - auto-kill on timeout."""
        try:
            start_time = datetime.now()

            result = subprocess.run(
                command,
                shell=True,
                timeout=timeout,
                capture_output=True,
                text=True,
                check=False
            )

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            return {
                "success": True,
                "command": command,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "duration": duration,
                "timeout": timeout,
                "killed_on_timeout": False,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "message": f"Command completed with exit code {result.returncode} in {duration:.2f}s"
            }

        except subprocess.TimeoutExpired as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            return {
                "success": False,
                "command": command,
                "exit_code": -1,
                "stdout": e.stdout or "",
                "stderr": e.stderr or "",
                "duration": duration,
                "timeout": timeout,
                "killed_on_timeout": True,
                "error": f"Command timed out after {timeout}s and was killed",
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "message": f"Command killed after {timeout}s timeout"
            }

        except Exception as e:
            return {
                "success": False,
                "command": command,
                "error": f"Failed to execute command: {str(e)}",
                "suggestions": [
                    "Check if the command syntax is correct",
                    "Verify that required programs are installed"
                ]
            }

    def _run_interactive(self, command: str, timeout: int) -> Dict[str, Any]:
        """Execute command in interactive mode - stream output, no auto-kill."""
        try:
            start_time = datetime.now()

            # Start process
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            # Store active process info
            self.active_process = {
                "process": process,
                "command": command,
                "start_time": start_time,
                "timeout": timeout,
                "stdout_lines": [],
                "stderr_lines": []
            }

            # Get initial output (wait briefly for process to start)
            time.sleep(0.1)
            initial_output = self.get_output()

            return {
                "success": True,
                "command": command,
                "mode": "interactive",
                "pid": process.pid,
                "timeout": timeout,
                "start_time": start_time.isoformat(),
                "initial_output": initial_output,
                "message": f"Interactive command started (PID: {process.pid}). Use get_output(), send_input(), or stop_process()."
            }

        except Exception as e:
            self.active_process = None
            return {
                "success": False,
                "command": command,
                "error": f"Failed to start interactive command: {str(e)}",
                "suggestions": [
                    "Check if the command is valid",
                    "Ensure required programs are installed"
                ]
            }

    def get_output(self, max_lines: int = 100) -> Dict[str, Any]:
        """Get current output from active interactive process."""
        if self.active_process is None:
            return {
                "success": False,
                "error": "No active interactive process",
                "suggestions": ["Start an interactive command first using run_command(..., interactive=True)"]
            }

        try:
            proc_info = self.active_process
            process = proc_info["process"]

            # Read available output
            new_stdout = []
            new_stderr = []

            # Non-blocking read from stdout
            if process.stdout and process.stdout.readable():
                try:
                    line = process.stdout.readline()
                    if line:
                        new_stdout.append(line.rstrip())
                        proc_info["stdout_lines"].append(line.rstrip())
                except:
                    pass

            # Non-blocking read from stderr
            if process.stderr and process.stderr.readable():
                try:
                    line = process.stderr.readline()
                    if line:
                        new_stderr.append(line.rstrip())
                        proc_info["stderr_lines"].append(line.rstrip())
                except:
                    pass

            # Check if process is still running
            return_code = process.poll()
            is_running = return_code is None

            # Clean up if process finished
            if not is_running:
                self.active_process = None

            # Get recent output (limited by max_lines)
            recent_stdout = proc_info["stdout_lines"][-max_lines:] if proc_info["stdout_lines"] else []
            recent_stderr = proc_info["stderr_lines"][-max_lines:] if proc_info["stderr_lines"] else []

            return {
                "success": True,
                "is_running": is_running,
                "return_code": return_code,
                "new_stdout": new_stdout,
                "new_stderr": new_stderr,
                "recent_stdout": recent_stdout,
                "recent_stderr": recent_stderr,
                "total_stdout_lines": len(proc_info["stdout_lines"]),
                "total_stderr_lines": len(proc_info["stderr_lines"]),
                "runtime": (datetime.now() - proc_info["start_time"]).total_seconds(),
                "message": f"Process {'running' if is_running else 'finished'}, {len(new_stdout)} new stdout, {len(new_stderr)} new stderr"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get process output: {str(e)}"
            }

    def send_input(self, input_text: str) -> Dict[str, Any]:
        """Send input to active interactive process."""
        if self.active_process is None:
            return {
                "success": False,
                "error": "No active interactive process"
            }

        try:
            process = self.active_process["process"]

            if process.poll() is not None:
                self.active_process = None
                return {
                    "success": False,
                    "error": "Process has already terminated",
                    "return_code": process.returncode
                }

            # Send input
            process.stdin.write(input_text + '\n')
            process.stdin.flush()

            return {
                "success": True,
                "input_sent": input_text,
                "message": f"Input sent to process"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to send input: {str(e)}"
            }

    def stop_process(self, force: bool = False) -> Dict[str, Any]:
        """Stop active interactive process."""
        if self.active_process is None:
            return {
                "success": False,
                "error": "No active interactive process"
            }

        try:
            process = self.active_process["process"]
            command = self.active_process["command"]

            if process.poll() is not None:
                # Process already terminated
                self.active_process = None
                return {
                    "success": True,
                    "message": f"Process was already terminated",
                    "return_code": process.returncode
                }

            # Stop the process
            if force:
                process.kill()  # SIGKILL
                method = "killed"
            else:
                process.terminate()  # SIGTERM
                method = "terminated"

            # Wait for process to stop (with timeout)
            try:
                return_code = process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if terminate didn't work
                process.kill()
                return_code = process.wait(timeout=5)
                method = "force killed"

            self.active_process = None

            return {
                "success": True,
                "command": command,
                "method": method,
                "return_code": return_code,
                "message": f"Process {method} successfully"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to stop process: {str(e)}"
            }

    def get_status(self) -> Dict[str, Any]:
        """Get status of active process."""
        if self.active_process is None:
            return {
                "success": True,
                "active_process": None,
                "message": "No active process"
            }

        try:
            proc_info = self.active_process
            process = proc_info["process"]
            return_code = process.poll()
            is_running = return_code is None

            # Clean up if finished
            if not is_running:
                self.active_process = None

            return {
                "success": True,
                "active_process": {
                    "command": proc_info["command"],
                    "pid": process.pid,
                    "is_running": is_running,
                    "return_code": return_code,
                    "start_time": proc_info["start_time"].isoformat(),
                    "runtime": (datetime.now() - proc_info["start_time"]).total_seconds(),
                    "stdout_lines": len(proc_info["stdout_lines"]),
                    "stderr_lines": len(proc_info["stderr_lines"])
                },
                "message": f"Process {'running' if is_running else 'finished'}"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get status: {str(e)}"
            }

