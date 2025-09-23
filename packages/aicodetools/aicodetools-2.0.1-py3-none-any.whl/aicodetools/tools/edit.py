"""
Edit Tool - Simplified file editing for AI agents.

Features:
- Simple string find-and-replace with automatic backup
- Read-first safety check
- Support for single or all occurrences
- Clear diff preview of changes
- Fixed UTF-8 encoding
"""

import os
import difflib
import shutil
from typing import Dict, Any, Set
from datetime import datetime


class EditTool:
    """Simplified file editing tool optimized for AI agents."""

    def __init__(self):
        self.read_files: Set[str] = set()

    def mark_file_as_read(self, file_path: str) -> None:
        """Mark a file as having been read (for safety checks)."""
        self.read_files.add(os.path.abspath(file_path))

    def has_been_read(self, file_path: str) -> bool:
        """Check if file has been read."""
        return os.path.abspath(file_path) in self.read_files

    def edit_file(self, file_path: str, old_string: str, new_string: str, replace_all: bool = False) -> Dict[str, Any]:
        """
        Replace text in file with automatic backup and read-first safety.

        Args:
            file_path: Path to file to edit
            old_string: Text to search for and replace
            new_string: Replacement text
            replace_all: If True, replace all occurrences; if False, replace first only

        Returns:
            Dict with edit results and metadata
        """
        try:
            abs_path = os.path.abspath(file_path)

            # Check file existence
            if not os.path.exists(abs_path):
                return {
                    "success": False,
                    "error": f"File not found: {file_path}",
                    "suggestions": [
                        "Check if file path is correct",
                        "Use write_file() to create the file first"
                    ]
                }

            # Safety check: require read-first
            if not self.has_been_read(abs_path):
                return {
                    "success": False,
                    "error": f"File not read first - read the file before editing: {file_path}",
                    "suggestions": [
                        "Use read_file() to examine content first",
                        "This prevents accidental modifications of important files"
                    ]
                }

            # Read current content with UTF-8
            try:
                with open(abs_path, 'r', encoding='utf-8') as f:
                    original_content = f.read()
            except UnicodeDecodeError:
                return {
                    "success": False,
                    "error": f"Unable to decode file as UTF-8: {file_path}",
                    "suggestions": [
                        "File may be binary or use different encoding",
                        "Ensure file contains valid UTF-8 text"
                    ]
                }

            # Check if old_string exists
            if old_string not in original_content:
                # Show first 100 chars for reference
                old_preview = old_string[:100] + ('...' if len(old_string) > 100 else '')
                return {
                    "success": False,
                    "error": f"Text to replace not found: '{old_preview}'",
                    "suggestions": [
                        "Check that text to replace is exactly correct",
                        "Use read_file() to verify current file content",
                        "Ensure whitespace and line endings match exactly"
                    ]
                }

            # Count occurrences
            occurrence_count = original_content.count(old_string)

            # Perform replacement
            if replace_all:
                new_content = original_content.replace(old_string, new_string)
                replacements_made = occurrence_count
            else:
                new_content = original_content.replace(old_string, new_string, 1)
                replacements_made = 1

            # Create backup before editing
            backup_path = self._create_backup(abs_path)

            # Generate diff preview
            diff_lines = list(difflib.unified_diff(
                original_content.splitlines(keepends=True),
                new_content.splitlines(keepends=True),
                fromfile=f"{file_path} (original)",
                tofile=f"{file_path} (modified)",
                lineterm=""
            ))

            preview = ''.join(diff_lines) if diff_lines else "No changes detected"

            # Write the modified content
            try:
                with open(abs_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)

                response = {
                    "success": True,
                    "file_path": file_path,
                    "old_string": old_string,
                    "new_string": new_string,
                    "replacements_made": replacements_made,
                    "total_occurrences": occurrence_count,
                    "replace_all": replace_all,
                    "preview": preview,
                    "bytes_changed": len(new_content.encode('utf-8')) - len(original_content.encode('utf-8'))
                }

                if backup_path:
                    response["backup_created"] = backup_path

                response["message"] = f"File edited successfully. Replaced {replacements_made} occurrence(s)."

                return response

            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to write modified content: {str(e)}",
                    "suggestions": [
                        "Check file permissions",
                        "Ensure file is not locked by another process"
                    ]
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Edit operation failed: {str(e)}",
                "suggestions": [
                    "Verify file path is correct",
                    "Check file permissions"
                ]
            }

    def _create_backup(self, file_path: str) -> str:
        """Create a timestamped backup of an existing file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{file_path}.backup_{timestamp}"

        try:
            shutil.copy2(file_path, backup_path)
            return backup_path
        except Exception:
            # If backup fails, return None but don't prevent the edit operation
            return None