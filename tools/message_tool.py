"""
Message tool adapter for Manus AI Clone
Implements secure messaging functionality with content filtering
"""

import re
import uuid
from typing import Dict, Any, Optional, List, Union

from core.event_processor import EventType
from tools.tool_interface import ToolAdapter, ToolType, ToolMetadata, ExecutionResult, SecurityContext, PermissionLevel

class MessageTool(ToolAdapter):
    """
    Adapter for messaging functionality with security validation
    """
    def __init__(self):
        # Create tool metadata
        metadata = ToolMetadata(
            name="message_tool",
            description="Send messages to users or external systems",
            version="1.0.0",
            author="Manus AI Clone Team",
            license_type="MIT"
        )
        
        # Initialize base class
        super().__init__(
            tool_type=ToolType.MESSAGE,
            metadata=metadata,
            permission_level=PermissionLevel.WRITE
        )
        
        # Message-specific configuration
        self.max_message_length = 10000  # characters
        self.prohibited_patterns = [
            r"password=.*",
            r"api_key=.*",
            r"secret=.*"
        ]
        self.supported_recipients = ["user", "system", "external"]

    def _validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """
        Validate message parameters
        
        Args:
            parameters: Parameters to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check required parameters
        required_fields = ["recipient", "text"]
        if not all(field in parameters for field in required_fields):
            return False
            
        # Validate recipient type
        if parameters["recipient"] not in self.supported_recipients:
            return False
            
        # Validate message length
        if len(parameters["text"]) > self.max_message_length:
            return False
            
        # Content filtering
        if not self._validate_content(parameters["text"]):
            return False
            
        return True

    def _validate_content(self, text: str) -> bool:
        """
        Validate message content against prohibited patterns
        
        Args:
            text: Message text to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check for prohibited patterns
        for pattern in self.prohibited_patterns:
            if re.search(pattern, text):
                return False
                
        return True

    def _execute_direct(self, parameters: Dict[str, Any]) -> ExecutionResult:
        """
        Send a message through the adapter
        
        Args:
            parameters: Dictionary containing message details
            
        Returns:
            Execution result
        """
        try:
            # Extract parameters
            recipient = parameters["recipient"]
            text = parameters["text"]
            attachments = parameters.get("attachments", [])
            
            # Simulate message delivery
            delivery_id = str(uuid.uuid4())
            
            # Return success result
            return ExecutionResult(
                tool_name=self.metadata.name,
                success=True,
                output={
                    "delivery_id": delivery_id,
                    "recipient": recipient,
                    "text_preview": text[:50] + ("..." if len(text) > 50 else ""),
                    "attachment_count": len(attachments)
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

    def send_message(self, 
                    recipient: str,
                    text: str,
                    attachments: Optional[List[Dict[str, Any]]] = None,
                    context: Optional[SecurityContext] = None) -> ExecutionResult:
        """
        Direct API for sending messages
        
        Args:
            recipient: Target for the message
            text: Content of the message
            attachments: Optional list of attachments
            context: Security context for operation validation
            
        Returns:
            Execution result
        """
        # Build parameters dictionary
        parameters = {
            "recipient": recipient,
            "text": text
        }
        
        if attachments:
            parameters["attachments"] = attachments
            
        # Execute through main execution path
        return self.execute(parameters, context)

    def add_prohibited_pattern(self, pattern: str) -> None:
        """
        Add a new prohibited content pattern
        
        Args:
            pattern: Regular expression pattern to block
        """
        self.prohibited_patterns.append(pattern)

    def set_max_message_length(self, length: int) -> None:
        """
        Set maximum allowed message length
        
        Args:
            length: Maximum length in characters
        """
        self.max_message_length = length