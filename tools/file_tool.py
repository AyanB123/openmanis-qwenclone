"""
File tool adapter for Manus AI Clone
Implements secure file operations with sandboxing
"""

import os
import re
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List, Union

from tools.tool_interface import ToolAdapter, ToolType, ToolMetadata, ExecutionResult, SecurityContext, PermissionLevel

class FileOperation(Enum):
    """Supported file operations"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    LIST = "list"
    SEARCH = "search"

class FileOperationType(Enum):
    """Supported file operations"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    LIST = "list"
    SEARCH = "search"


class FileTool(ToolAdapter):
    """
    Adapter for secure file operations with sandboxing
    """
    def __init__(self):
        # Create tool metadata
        metadata = ToolMetadata(
            name="file_tool",
            description="Secure file operations with sandboxed execution",
            version="1.0.0",
            author="Manus AI Clone Team",
            license_type="MIT"
        )
        
        # Initialize base class
        super().__init__(
            tool_type=ToolType.FILE,
            metadata=metadata,
            permission_level=PermissionLevel.WRITE
        )
        
        # File-specific configuration
        self.sandbox_root = "/sandbox/files"
        self.max_file_size = 10 * 1024 * 1024  # bytes (10MB)
        self.allowed_extensions = [".txt", ".md", ".log"]
        self.prohibited_patterns = [
            r".*\.env$",
            r".*\.pem$",
            r".*\.key$"
        ]
        self.read_only_paths = ["system/config/", "data/reference/"]
        
        # Add missing attributes from the reference implementation
        self.file_system = {}  # type: Dict[str, Dict[str, Any]]
        self.usage_stats = {
            "total_operations": 0,
            "successful_operations": 0,
            "failed_operations": 0,
            "last_reset": datetime.now().isoformat()
        }

    def _validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """
        Validate file operation parameters
        
        Args:
            parameters: Parameters to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check required parameters
        if "operation" not in parameters:
            return False
            
        # Validate operation type
        try:
            operation = FileOperation(parameters["operation"])
        except ValueError:
            return False
            
        # Validate path parameter for all operations
        if "path" not in parameters and operation != FileOperation.LIST:
            return False
            
        # Operation-specific validation
        if operation == FileOperation.READ:
            return "path" in parameters
            
        elif operation == FileOperation.WRITE:
            if not all(key in parameters for key in ["path", "content"]):
                return False
            if len(parameters["content"]) > self.max_file_size:
                return False
            
        elif operation == FileOperation.DELETE:
            if not self._validate_deletion(parameters["path"]):
                return False
            
        elif operation == FileOperation.SEARCH:
            if "pattern" not in parameters:
                return False
            
        return True

    def _validate_deletion(self, path: str) -> bool:
        """
        Validate deletion operation against security rules
        
        Args:
            path: Path to check
            
        Returns:
            True if deletion is allowed
        """
        # Prevent deletion of read-only paths
        for read_only_path in self.read_only_paths:
            if path.startswith(read_only_path):
                return False
                
        return True

    def _validate_path(self, path: str) -> bool:
        """
        Validate path against security constraints
        
        Args:
            path: Path to validate
            
        Returns:
            True if path is valid and accessible
        """
        # Prevent path traversal attacks
        if ".." in path:
            return False
            
        # Check prohibited patterns
        for pattern in self.prohibited_patterns:
            if re.search(pattern, path):
                return False
                
        return True

    def _execute_direct(self, parameters: Dict[str, Any]) -> ExecutionResult:
        """
        Execute file operation based on parameters
        
        Args:
            parameters: Dictionary containing operation details
            
        Returns:
            Execution result
        """
        try:
            # Parse operation
            operation = FileOperation(parameters["operation"])
            
            # Common parameters
            path = parameters.get("path")
            
            # Execute operation
            if operation == FileOperation.READ:
                return self._handle_read(parameters)
                
            elif operation == FileOperation.WRITE:
                return self._handle_write(parameters)
                
            elif operation == FileOperation.DELETE:
                return self._handle_delete(parameters)
                
            elif operation == FileOperation.LIST:
                return self._handle_list(parameters)
                
            elif operation == FileOperation.SEARCH:
                return self._handle_search(parameters)
                
            # Unknown operation
            return ExecutionResult(
                tool_name=self.metadata.name,
                success=False,
                output=None,
                error=f"Unsupported operation: {operation.value}"
            )
            
        except Exception as e:
            return ExecutionResult(
                tool_name=self.metadata.name,
                success=False,
                output=None,
                error=str(e)
            )

    def _handle_read(self, params: Dict[str, Any]) -> ExecutionResult:
        """
        Handle file read operation
        
        Args:
            params: Operation parameters
            
        Returns:
            Execution result
        """
        # Extract parameters
        path = params["path"]
        start_line = params.get("start_line")
        end_line = params.get("end_line")
        
        # Validate path
        if not self._validate_path(path):
            raise ValueError(f"Invalid path: {path}")
            
        # Simulate reading file
        content = f"// ... content of {path} ..."
        line_count = 100  # Simulated line count
        
        # Apply line range if specified
        if start_line is not None or end_line is not None:
            lines = content.split("\n")
            start = start_line if start_line is not None else 0
            end = end_line if end_line is not None else len(lines)
            content = "\n".join(lines[start:end])
            
        # Return result
        return ExecutionResult(
            tool_name=self.metadata.name,
            success=True,
            output={
                "path": path,
                "content": content,
                "size": len(content),
                "line_count": line_count
            }
        )

    def _handle_write(self, params: Dict[str, Any]) -> ExecutionResult:
        """
        Handle file write operation
        
        Args:
            params: Operation parameters
            
        Returns:
            Execution result
        """
        # Extract parameters
        path = params["path"]
        content = params["content"]
        mode = params.get("mode", "w")
        
        # Validate path
        if not self._validate_path(path):
            raise ValueError(f"Invalid path: {path}")
            
        # Validate content size
        if len(content) > self.max_file_size:
            raise ValueError(f"Content exceeds maximum size ({self.max_file_size} bytes)")
            
        # Validate file extension
        _, ext = os.path.splitext(path)
        if ext not in self.allowed_extensions:
            raise ValueError(f"Extension {ext} not allowed")
            
        # Simulate writing file
        # In real implementation, this would use the sandbox
        return ExecutionResult(
            tool_name=self.metadata.name,
            success=True,
            output={
                "path": path,
                "written_chars": len(content),
                "mode": mode
            }
        )

    def _handle_delete(self, params: Dict[str, Any]) -> ExecutionResult:
        """
        Handle file delete operation
        
        Args:
            params: Operation parameters
            
        Returns:
            Execution result
        """
        # Extract parameters
        path = params["path"]
        
        # Validate path
        if not self._validate_path(path):
            raise ValueError(f"Invalid path: {path}")
            
        # Validate deletion permissions
        if not self._validate_deletion(path):
            raise ValueError(f"Deletion not allowed for {path}")
            
        # Simulate deletion
        return ExecutionResult(
            tool_name=self.metadata.name,
            success=True,
            output={
                "path": path,
                "deleted_at": datetime.now().isoformat()
            }
        )

    def _handle_list(self, params: Dict[str, Any]) -> ExecutionResult:
        """
        Handle file list operation
        
        Args:
            params: Operation parameters
            
        Returns:
            Execution result
        """
        # Simulate directory listing
        return ExecutionResult(
            tool_name=self.metadata.name,
            success=True,
            output={
                "path": params.get("path", self.sandbox_root),
                "files": [
                    {"name": "file1.txt", "size": 1024, "modified": "2023-05-01T12:00:00Z"},
                    {"name": "notes.md", "size": 2048, "modified": "2023-05-01T12:00:00Z"}
                ],
                "directories": ["docs", "data"]
            }
        )

    def _handle_search(self, params: Dict[str, Any]) -> ExecutionResult:
        """
        Handle file search operation
        
        Args:
            params: Operation parameters
            
        Returns:
            Execution result
        """
        # Extract parameters
        pattern = params["pattern"]
        path = params.get("path", self.sandbox_root)
        
        # Validate path
        if not self._validate_path(path):
            raise ValueError(f"Invalid path: {path}")
            
        # Simulate search results
        return ExecutionResult(
            tool_name=self.metadata.name,
            success=True,
            output={
                "path": path,
                "pattern": pattern,
                "results": [
                    {
                        "file": "example.txt",
                        "matches": [
                            {"line": 10, "text": "... matching text ..."}
                        ]
                    }
                ]
            }
        )

    def set_sandbox_config(self, 
                         max_file_size: int = 10 * 1024 * 1024, 
                         allowed_extensions: List[str] = [".txt", ".md", ".log"],
                         read_only_paths: List[str] = []) -> None:
        """
        Configure sandbox settings for file operations
        
        Args:
            max_file_size: Maximum allowed file size in bytes
            allowed_extensions: List of allowed file extensions
            read_only_paths: List of read-only paths
        """
        self.max_file_size = max_file_size
        self.allowed_extensions = allowed_extensions
        self.read_only_paths = read_only_paths

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics for file operations"""
        return self.usage_stats

    def reset_usage_stats(self) -> None:
        """Reset usage statistics"""
        self.usage_stats = {
            "total_operations": 0,
            "successful_operations": 0,
            "failed_operations": 0,
            "last_reset": datetime.now().isoformat()
        }

    def get_file_stats(self, path: str) -> Dict[str, Any]:
        """
        Get statistics for a file
        
        Args:
            path: Path to get stats for
            
        Returns:
            Dictionary with file statistics
        """
        # In real implementation, would retrieve actual file stats
        return {
            "path": path,
            "exists": True,
            "is_directory": False,
            "size": 1024,
            "modified": datetime.now().isoformat()
        }