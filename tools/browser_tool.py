"""
Browser tool adapter for Manus AI Clone
Implements standardized interface for browser operations
"""

import re
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Union

from tools.tool_interface import ToolAdapter, ToolType, ToolMetadata, ExecutionResult, SecurityContext, PermissionLevel

class BrowserTool(ToolAdapter):
    """
    Adapter for secure web browsing operations
    """
    def __init__(self):
        # Create tool metadata
        metadata = ToolMetadata(
            name="browser_tool",
            description="Secure web browsing with content filtering",
            version="1.0.0",
            author="Manus AI Clone Team",
            license_type="MIT"
        )
        
        # Initialize base class
        super().__init__(
            tool_type=ToolType.BROWSER,
            metadata=metadata,
            permission_level=PermissionLevel.WRITE
        )
        
        # Browser-specific configuration
        self.sandbox_config = {
            "memory_limit": 512 * 1024 * 1024,  # bytes (512MB)
            "timeout": 30.0,  # seconds
            "max_redirects": 5,
            "allowed_domains": ["example.com", "trusted.org"],
            "content_types_allowed": ["text/html", "application/json"]
        }
        
        # Prohibited patterns
        self.prohibited_patterns = [
            r"login.*password",
            r"account.*details",
            r"credit-card.*information"
        ]
        
        # Blocked domains
        self.blocked_domains = [
            "malicious.com",
            "phishing.net"
        ]

    def _validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """
        Validate browser command parameters
        
        Args:
            parameters: Parameters to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check required parameter
        if "url" not in parameters:
            return False
            
        # Validate URL format
        if not isinstance(parameters["url"], str):
            return False
            
        # Additional validation could be added here
        return True

    def _validate_url(self, url: str) -> bool:
        """
        Validate URL against security rules
        
        Args:
            url: URL to validate
            
        Returns:
            True if URL is allowed
        """
        # Basic URL pattern validation
        url_pattern = r"^https?://[a-zA-Z0-9.-]+.[a-zA-Z]{2,}(:[0-9]+)?(/.*)?$"
        if not re.match(url_pattern, url):
            return False
            
        # Extract domain from URL
        domain = self._extract_domain(url)
        
        # Check blocked domains
        if any(blocked in domain for blocked in self.blocked_domains):
            return False
            
        # Check allowed domains
        if self.sandbox_config["allowed_domains"] and not any(
            allowed in domain for allowed in self.sandbox_config["allowed_domains"]):
            return False
            
        # Content type validation
        content_type = parameters.get("content_type")
        if content_type and content_type not in self.sandbox_config["content_types_allowed"]:
            return False
            
        return True

    def _extract_domain(self, url: str) -> str:
        """
        Extract domain from a URL
        
        Args:
            url: Full URL string
            
        Returns:
            Extracted domain
        """
        # Simple domain extraction
        start = url.find("//") + 2
        end = url.find("/", start)
        if end == -1:
            end = len(url)
            
        return url[start:end].lower()
        
    def _create_error_response(self, message: str) -> Dict[str, Any]:
        """
        Create standardized error response
        
        Args:
            message: Error message
            
        Returns:
            Error response dictionary
        """
        return {
            "status": "error",
            "message": message,
            "timestamp": datetime.now().isoformat()
        }

    def _execute_in_sandbox(self, parameters: Dict[str, Any]) -> ExecutionResult:
        """
        Execute browser operation in sandboxed environment
        
        Args:
            parameters: Dictionary containing operation details
            
        Returns:
            Execution result
        """
        try:
            # Extract parameters
            url = parameters["url"]
            method = parameters.get("method", "GET")
            headers = parameters.get("headers", {})
            
            # Simulate request execution
            # In real implementation, this would use a secure browser sandbox
            response_content = f"// ... content from '{url}' ..."
            
            # Return success result
            return ExecutionResult(
                tool_name=self.metadata.name,
                success=True,
                output={
                    "url": url,
                    "method": method,
                    "content_preview": response_content[:200] + ("..." if len(response_content) > 200 else ""),
                    "content_length": len(response_content)
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

    def browse_url(self, 
                  url: str,
                  method: str = "GET",
                  headers: Optional[Dict[str, Any]] = None,
                  context: Optional[SecurityContext] = None) -> ExecutionResult:
        """
        Direct API for browsing URLs
        
        Args:
            url: URL to access
            method: HTTP method (GET, POST, etc.)
            headers: Optional request headers
            context: Security context for operation validation
            
        Returns:
            Execution result
        """
        # Build parameters dictionary
        parameters = {
            "url": url,
            "method": method
        }
        
        if headers:
            parameters["headers"] = headers
            
        # Execute through main execution path
        return self.execute(parameters, context)

    def set_sandbox_config(self, 
                         memory_limit: int = 512 * 1024 * 1024, 
                         timeout: float = 30.0,
                         max_redirects: int = 5,
                         allowed_domains: Optional[List[str]] = None,
                         content_types_allowed: Optional[List[str]] = None) -> None:
        """
        Configure sandbox settings
        
        Args:
            memory_limit: Maximum memory usage in bytes
            timeout: Maximum execution time in seconds
            max_redirects: Maximum number of allowed redirects
            allowed_domains: List of allowed domains
            content_types_allowed: List of allowed content types
        """
        config_update = {
            "memory_limit": memory_limit,
            "timeout": timeout,
            "max_redirects": max_redirects
        }
        
        if allowed_domains is not None:
            config_update["allowed_domains"] = allowed_domains
            
        if content_types_allowed is not None:
            config_update["content_types_allowed"] = content_types_allowed
            
        self.sandbox_config.update(config_update)

    def add_blocked_domain(self, domain: str) -> None:
        """
        Add a new domain to block
        
        Args:
            domain: Domain to block
        """
        self.blocked_domains.append(domain.lower())

    def remove_blocked_domain(self, domain: str) -> None:
        """
        Remove a domain from the block list
        
        Args:
            domain: Domain to unblock
        """
        domain_lower = domain.lower()
        self.blocked_domains = [d for d in self.blocked_domains if d != domain_lower]

    def add_allowed_domain(self, domain: str) -> None:
        """
        Add a new domain to allow
        
        Args:
            domain: Domain to allow
        """
        self.sandbox_config["allowed_domains"].append(domain.lower())

    def remove_allowed_domain(self, domain: str) -> None:
        """
        Remove a domain from allowed list
        
        Args:
            domain: Domain to remove
        """
        domain_lower = domain.lower()
        self.sandbox_config["allowed_domains"] = [
            d for d in self.sandbox_config["allowed_domains"] if d != domain_lower
        ]