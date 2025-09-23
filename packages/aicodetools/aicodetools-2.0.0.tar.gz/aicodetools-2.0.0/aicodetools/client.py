"""
AI Code Tools Client - Python interface for communicating with the server.

Provides a simple Python API that communicates with the Docker-based server
via HTTP requests. Handles connection management and response formatting.
"""

import json
import time
import subprocess
import requests
from typing import Dict, Any, Optional, List
import os
import logging


class CodeToolsClient:
    """Client interface for AI Code Tools server."""

    def __init__(self, server_url: str = "http://localhost:18080", auto_start: bool = True,
                 docker_image: str = "aicodetools:latest", port: int = 18080):
        self.server_url = server_url.rstrip('/')
        self.session = requests.Session()
        self.docker_container = None
        self.docker_image = docker_image
        self.port = port

        if auto_start:
            self._ensure_server_running()

    def _ensure_server_running(self) -> bool:
        """Ensure the server is running, start if necessary."""
        try:
            # Check if server is already running
            response = self.session.get(f"{self.server_url}/api/status", timeout=2)
            if response.status_code == 200:
                logging.info("Server is already running")
                return True
        except requests.exceptions.RequestException:
            pass

        # Try to start server using Docker
        return self._start_docker_server()

    def _start_docker_server(self) -> bool:
        """Start the server using Docker."""
        try:
            logging.info("Starting AI Code Tools server in Docker...")

            # Check if Docker service is running
            try:
                result = subprocess.run(['docker', 'info'], capture_output=True, text=True, timeout=10)
                if result.returncode != 0:
                    logging.error("Docker service is not running. Please start Docker.")
                    return False
            except (subprocess.TimeoutExpired, FileNotFoundError):
                logging.error("Docker not found or not running. Please install and start Docker.")
                return False

            # Get the directory containing this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)

            # Check if Docker image exists
            check_result = subprocess.run(['docker', 'images', '-q', self.docker_image],
                                        capture_output=True, text=True, timeout=10)

            if not check_result.stdout.strip():
                # Image doesn't exist
                if self.docker_image == "aicodetools:latest":
                    # Build default image
                    dockerfile_path = os.path.join(project_root, 'docker', 'Dockerfile')
                    if not os.path.exists(dockerfile_path):
                        logging.error(f"Dockerfile not found at: {dockerfile_path}")
                        return False

                    logging.info(f"Building image with: docker build -t aicodetools:latest {os.path.join(project_root, 'docker')}")
                    build_result = subprocess.run([
                        'docker', 'build', '-t', 'aicodetools:latest',
                        '-f', dockerfile_path, os.path.join(project_root, 'docker')
                    ], capture_output=True, text=True, timeout=300)

                    if build_result.returncode != 0:
                        logging.error(f"Build failed: {build_result.stderr}")
                        return False
                else:
                    # Try to pull custom image
                    logging.info(f"Pulling image: docker pull {self.docker_image}")
                    pull_result = subprocess.run(['docker', 'pull', self.docker_image],
                                               capture_output=True, text=True, timeout=120)
                    if pull_result.returncode != 0:
                        logging.error(f"Image '{self.docker_image}' not found. Please ensure it exists.")
                        return False

            # Clean up existing container
            subprocess.run(['docker', 'stop', 'aicodetools-container'], capture_output=True, text=True, timeout=10)
            subprocess.run(['docker', 'rm', 'aicodetools-container'], capture_output=True, text=True, timeout=10)

            # Start container
            run_cmd = [
                'docker', 'run', '-d', '--name', 'aicodetools-container',
                '-p', f'{self.port}:8080', '-v', f"{project_root}:/workspace/project",
                self.docker_image, 'python', '/workspace/project/aicodetools/server.py'
            ]

            logging.info(f"Starting container: docker run -p {self.port}:8080 {self.docker_image}")
            run_result = subprocess.run(run_cmd, capture_output=True, text=True, timeout=30)
            if run_result.returncode != 0:
                if "port is already allocated" in run_result.stderr:
                    logging.error(f"Port {self.port} is in use. Please stop other services or use a different port.")
                elif "permission denied" in run_result.stderr:
                    logging.error("Docker permission denied. Try running as administrator or add user to docker group.")
                else:
                    logging.error(f"Container failed to start: {run_result.stderr}")
                return False

            self.docker_container = 'aicodetools-container'

            # Wait for server to start
            for _ in range(30):  # Wait up to 30 seconds
                try:
                    response = self.session.get(f"{self.server_url}/api/status", timeout=2)
                    if response.status_code == 200:
                        logging.info("Server started successfully")
                        return True
                except requests.exceptions.RequestException:
                    pass
                time.sleep(1)

            logging.error("Server failed to start within timeout")
            return False

        except Exception as e:
            logging.error(f"Failed to start Docker server: {e}")
            return False

    def _make_request(self, endpoint: str, data: Optional[Dict[str, Any]] = None, method: str = 'POST') -> Dict[str, Any]:
        """Make HTTP request to server."""
        try:
            url = f"{self.server_url}/api/{endpoint}"

            if method == 'GET':
                response = self.session.get(url, timeout=30)
            else:
                response = self.session.post(url, json=data or {}, timeout=30)

            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            return {"success": False, "error": "Request timed out"}
        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "Failed to connect to server"}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Request failed: {str(e)}"}
        except json.JSONDecodeError:
            return {"success": False, "error": "Invalid JSON response from server"}

    # File Operations

    def read_file(self, file_path: str, lines_start: Optional[int] = None,
                  lines_end: Optional[int] = None, complete_lines: bool = False,
                  regex: Optional[str] = None) -> Dict[str, Any]:
        """
        Simplified file reading with smart token management.

        Args:
            file_path: Path to file to read
            lines_start: Starting line number (1-based) for LineArgs mode
            lines_end: Ending line number for LineArgs mode
            complete_lines: Use tiered approach to avoid splitting long lines
            regex: Regex pattern for RegexArgs mode

        Returns:
            Dict with content and metadata
        """
        data = {"file_path": file_path}

        if regex:
            # RegexArgs mode
            data["regex"] = regex
        elif lines_start is not None:
            # LineArgs mode
            data["lines_start"] = lines_start
            if lines_end is not None:
                data["lines_end"] = lines_end
            if complete_lines:
                data["complete_lines"] = complete_lines
        # If neither regex nor lines_start, it's full file read

        return self._make_request("read", data)

    def read_with_regex(self, file_path: str, pattern: str) -> Dict[str, Any]:
        """Read file and extract regex matches with smart context management."""
        return self.read_file(file_path, regex=pattern)

    def read_lines(self, file_path: str, start: int, end: Optional[int] = None,
                   complete_lines: bool = False) -> Dict[str, Any]:
        """Read specific line range from file."""
        return self.read_file(file_path, lines_start=start, lines_end=end, complete_lines=complete_lines)

    def write_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """
        Write content to file with automatic backup and read-first safety.

        Args:
            file_path: Path to file to write
            content: Content to write to file

        Returns:
            Dict with success status and metadata
        """
        data = {"file_path": file_path, "content": content}
        return self._make_request("write", data)

    def edit_file(self, file_path: str, old_string: str, new_string: str,
                  replace_all: bool = False) -> Dict[str, Any]:
        """
        Edit file using string replacement with automatic backup.

        Args:
            file_path: Path to file to edit
            old_string: Text to search for and replace
            new_string: Replacement text
            replace_all: If True, replace all occurrences; if False, replace first only

        Returns:
            Dict with edit results and diff preview
        """
        data = {
            "file_path": file_path,
            "old_string": old_string,
            "new_string": new_string,
            "replace_all": replace_all
        }
        return self._make_request("edit", data)

    # Command Execution

    def run_command(self, command: str, timeout: int = 300, interactive: bool = False) -> Dict[str, Any]:
        """Run command with simplified interface."""
        data = {
            "command": command,
            "timeout": timeout,
            "interactive": interactive
        }
        return self._make_request("run", data)

    def get_output(self, max_lines: int = 100) -> Dict[str, Any]:
        """Get output from active interactive process."""
        data = {"max_lines": max_lines}
        return self._make_request("get_output", data)

    def send_input(self, input_text: str) -> Dict[str, Any]:
        """Send input to active interactive process."""
        data = {"input_text": input_text}
        return self._make_request("send_input", data)

    def stop_process(self, force: bool = False) -> Dict[str, Any]:
        """Stop active interactive process."""
        data = {"force": force}
        return self._make_request("stop_process", data)

    def get_process_status(self) -> Dict[str, Any]:
        """Get status of active process."""
        return self._make_request("get_status", method='GET')

    # Server Management

    def get_status(self) -> Dict[str, Any]:
        """Get server status."""
        return self._make_request("status", method='GET')

    def stop_server(self) -> bool:
        """Stop the Docker server."""
        if self.docker_container:
            try:
                result = subprocess.run(['docker', 'stop', self.docker_container],
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    subprocess.run(['docker', 'rm', self.docker_container],
                                 capture_output=True, text=True)
                    self.docker_container = None
                    return True
            except Exception as e:
                logging.error(f"Failed to stop server: {e}")

        return False

    def restart_server(self) -> bool:
        """Restart the Docker server."""
        self.stop_server()
        time.sleep(2)
        return self._ensure_server_running()

    # Context Manager Support

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_server()

    # High-level helper methods

    def execute_script(self, script_content: str, script_name: str = "temp_script.py") -> Dict[str, Any]:
        """Write and execute a script."""
        # Write script
        write_result = self.write_file(script_name, script_content)
        if not write_result.get("success"):
            return write_result

        # Execute script
        run_result = self.run_command(f"python {script_name}")

        # Combine results
        return {
            "success": run_result.get("success", False),
            "script_name": script_name,
            "write_result": write_result,
            "run_result": run_result,
            "output": run_result.get("stdout", ""),
            "error": run_result.get("stderr", "")
        }

    def read_and_edit(self, file_path: str, old_string: str, new_string: str,
                     replace_all: bool = False) -> Dict[str, Any]:
        """Read file, then edit it (safe workflow)."""
        # First read the file (this marks it as read for safety)
        read_result = self.read_file(file_path)
        if not read_result.get("success"):
            return read_result

        # Then edit it (will work because file was read first)
        edit_result = self.edit_file(file_path, old_string, new_string, replace_all)

        return {
            "success": edit_result.get("success", False),
            "read_result": read_result,
            "edit_result": edit_result,
            "file_path": file_path,
            "message": f"Read and edit workflow completed. File {'modified' if edit_result.get('success') else 'unchanged'}."
        }

    def read_and_write(self, file_path: str, new_content: str) -> Dict[str, Any]:
        """Read file, then overwrite it (safe workflow)."""
        # First read the file (this marks it as read for safety)
        read_result = self.read_file(file_path)
        if not read_result.get("success"):
            return read_result

        # Then write new content (will work because file was read first)
        write_result = self.write_file(file_path, new_content)

        return {
            "success": write_result.get("success", False),
            "read_result": read_result,
            "write_result": write_result,
            "file_path": file_path,
            "message": f"Read and write workflow completed. File {'updated' if write_result.get('success') else 'unchanged'}."
        }