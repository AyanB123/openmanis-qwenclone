"""
Shell tool adapter for Manus AI Clone
Implements secure command execution with sandboxing
"""

import re
from typing import Dict, Any, Optional, List, Union

from core.event_processor import EventType
from tools.tool_interface import ToolAdapter, ToolType, ToolMetadata, ExecutionResult, SecurityContext, PermissionLevel

class ShellTool(ToolAdapter):
    """
    Adapter for secure shell command execution
    """
    def __init__(self):
        # Create tool metadata
        metadata = ToolMetadata(
            name="shell_tool",
            description="Execute shell commands in secure sandboxed environment",
            version="1.0.0",
            author="Manus AI Clone Team",
            license_type="MIT"
        )
        
        # Initialize base class
        super().__init__(
            tool_type=ToolType.SHELL,
            metadata=metadata,
            permission_level=PermissionLevel.ADMIN
        )
        
        # Shell-specific configuration
        self.sandbox_config = {
            "memory_limit": 512 * 1024 * 1024,  # bytes (512MB)
            "cpu_limit": 1.0,  # CPU time in seconds
            "network_access": False,
            "filesystem_readonly": True,
            "timeout": 30.0  # seconds
        }
        
        # Prohibited commands
        self.prohibited_patterns = [
            r"rm -rf.*",
            r"mkfs.*",
            r"dd if=.*",
            r"chmod.*777.*",
            r"chown.*root.*"
        ]
        
        # Allowed command patterns
        self.allowed_patterns = [
            r"^echo .*$",
            r"^cat .*$",
            r"^grep .*$",
            r"^find .*$",
            r"^ls .*$"
        ]

    def _validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """
        Validate shell command parameters
        
        Args:
            parameters: Parameters to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check required parameter
        if "command" not in parameters:
            return False
            
        # Validate command format
        if not isinstance(parameters["command"], str):
            return False
            
        # Validate working directory if present
        if "working_dir" in parameters and not self._validate_path(parameters["working_dir"]):
            return False
            
        # Validate command against security rules
        if not self._validate_command(parameters["command"]):
            return False
            
        return True

    def _validate_command(self, command: str) -> bool:
        """
        Validate command against prohibited patterns
        
        Args:
            command: Command string to validate
            
        Returns:
            True if command is allowed
        """
        # Check prohibited patterns
        for pattern in self.prohibited_patterns:
            if re.search(pattern, command):
                return False
                
        # If allowed patterns exist, command must match one
        if self.allowed_patterns:
            matched = any(re.search(pattern, command) for pattern in self.allowed_patterns)
            if not matched:
                return False
                
        # Additional validation could be added here
        return True

    def _validate_path(self, path: str) -> bool:
        """
        Validate file paths in shell commands
        
        Args:
            path: Path to validate
            
        Returns:
            True if path is valid and accessible
        """
        # Prevent path traversal attacks
        if ".." in path:
            return False
            
        # Allow only specific directories
        allowed_prefixes = ["/sandbox", "/tmp"]
        return any(path.startswith(prefix) for prefix in allowed_prefixes)

    def _execute_in_sandbox(self, parameters: Dict[str, Any]) -> ExecutionResult:
        """
        Execute command in sandboxed environment
        
        Args:
            parameters: Dictionary containing command details
            
        Returns:
            Execution result
        """
        try:
            # Extract parameters
            command = parameters["command"]
            working_dir = parameters.get("working_dir", "/sandbox")
            
            # Validate working directory
            if not self._validate_path(working_dir):
                raise ValueError(f"Invalid working directory: {working_dir}")
                
            # Simulate sandbox execution
            # In real implementation, this would use Docker or similar
            output = f"// ... output of '{command}' ..."
            
            # Return success result
            return ExecutionResult(
                tool_name=self.metadata.name,
                success=True,
                output={
                    "command": command,
                    "output": output,
                    "working_dir": working_dir
                }
            )
            
        except Exception as e:
            # Return failure result
            return ExecutionResult(
                tool_name=self.metadata.name,
                success=False,
                output=None,
                error=str(e)
            )

    def execute_shell_command(self, 
                             command: str,
                             working_dir: str = "/sandbox",
                             context: Optional[SecurityContext] = None) -> ExecutionResult:
        """
        Direct API for executing shell commands
        
        Args:
            command: Shell command to execute
            working_dir: Working directory for execution
            context: Security context for operation validation
            
        Returns:
            Execution result
        """
        # Build parameters dictionary
        parameters = {
            "command": command,
            "working_dir": working_dir
        }
        
        # Execute through main execution path
        return self.execute(parameters, context)

    def set_sandbox_config(self, 
                         memory_limit: int = 512 * 1024 * 1024, 
                         cpu_limit: float = 1.0,
                         network_access: bool = False,
                         filesystem_readonly: bool = True,
                         timeout: float = 30.0) -> None:
        """
        Configure sandbox settings
        
        Args:
            memory_limit: Maximum memory usage in bytes
            cpu_limit: Maximum CPU time in seconds
            network_access: Whether network access is allowed
            filesystem_readonly: Whether filesystem is read-only
            timeout: Maximum execution time in seconds
        """
        self.sandbox_config.update({
            "memory_limit": memory_limit,
            "cpu_limit": cpu_limit,
            "network_access": network_access,
            "filesystem_readonly": filesystem_readonly,
            "timeout": timeout
        })

    def add_prohibited_pattern(self, pattern: str) -> None:
        """
        Add a new prohibited command pattern
        
        Args:
            pattern: Regular expression pattern to block
        """
        self.prohibited_patterns.append(pattern)

    def add_allowed_pattern(self, pattern: str) -> None:
        """
        Add a new allowed command pattern
        
        Args:
            pattern: Regular expression pattern to allow
        """
        self.allowed_patterns.append(pattern)

    def remove_allowed_pattern(self, pattern: str) -> None:
        """
        Remove an allowed command pattern
        
        Args:
            pattern: Pattern to remove
        """
        if pattern in self.allowed_patterns:
            self.allowed_patterns.remove(pattern)