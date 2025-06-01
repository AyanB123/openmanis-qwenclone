"""
Security context management for Manus AI Clone
Implements security context with validation
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

from security.permission_validator import PermissionValidator, SecurityContext, AccessRuleManager

class SecurityContext:
    """
    Represents a security context with user information and permissions
    """
    def __init__(self, 
                 user_id: str,
                 roles: List[str],
                 ip_address: str,
                 session_id: Optional[str] = None,
                 validator: Optional[PermissionValidator] = None):
        self.user_id = user_id
        self.roles = roles
        self.ip_address = ip_address
        self.session_id = session_id or str(uuid.uuid4())
        self.validator = validator or PermissionValidator()
        self.created_at = datetime.now().isoformat()
        self.last_active = self.created_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary representation"""
        return {
            "user_id": self.user_id,
            "roles": self.roles,
            "ip_address": self.ip_address,
            "session_id": self.session_id,
            "created_at": self.created_at,
            "last_active": self.last_active
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SecurityContext':
        """Create context from dictionary"""
        return cls(
            user_id=data["user_id"],
            roles=data["roles"],
            ip_address=data["ip_address"],
            session_id=data.get("session_id"),
            validator=None  # Would need to be re-established from context
        )

    def update_activity(self) -> None:
        """Update last activity timestamp"""
        self.last_active = datetime.now().isoformat()

    def validate_permission(self, required_level: int) -> bool:
        """
        Validate if the context has sufficient permission
        
        Args:
            required_level: Required permission level
            
        Returns:
            True if permitted
        """
        # In real implementation would check actual permissions
        return True

    def check_operation_permission(self, operation: str) -> bool:
        """
        Check if the context has permission for an operation
        
        Args:
            operation: Operation type
            
        Returns:
            True if permitted
        """
        # In real implementation would check operation-specific permissions
        return True

    def set_logger(self, logger_function: callable) -> None:
        """
        Set a logger function for this context
        
        Args:
            logger_function: Function to call for logging events
        """
        self.logger = logger_function

    def log_security_event(self, message: str, event_type: str) -> None:
        """
        Log a security-related event
        
        Args:
            message: Event description
            event_type: Type of event
        """
        # If logger is available, use it
        if hasattr(self, "logger") and self.logger:
            self.logger(message=message, event_type=event_type)
        # Otherwise fall back to default logging
        else:
            print(f"SECURITY EVENT [{event_type}]: {message}")

class SecurityContextValidator:
    """
    Validates security contexts and permissions
    """
    def __init__(self):
        # Default permission level
        self.default_permission = PermissionLevel.READ
        
        # Security policies
        self.policies = {
            "session_timeout": 3600,  # seconds
            "max_attempts": 5,
            "lockout_period": 300  # seconds
        }
        
        # Active sessions
        self.sessions = {}  # type: Dict[str, SecurityContext]
        
        # Security rules
        self.rule_manager = AccessRuleManager()

    def create_context(self, 
                      user_id: str,
                      roles: List[str],
                      ip_address: str,
                      session_id: Optional[str] = None) -> SecurityContext:
        """
        Create a new security context
        
        Args:
            user_id: User identifier
            roles: User roles
            ip_address: User IP address
            session_id: Optional session ID
            
        Returns:
            Created security context
        """
        # Generate session ID if not provided
        session_id = session_id or str(uuid.uuid4())
        
        # Create validator
        validator = PermissionValidator(
            rule_manager=self.rule_manager
        )
        
        # Create context
        context = SecurityContext(
            user_id=user_id,
            roles=roles,
            session_id=session_id,
            ip_address=ip_address,
            validator=validator
        )
        
        # Store session
        self.sessions[session_id] = context
        
        return context

    def validate_operation(self, 
                         operation: Dict[str, Any],
                         context: SecurityContext,
                         required_level: PermissionLevel = PermissionLevel.READ) -> bool:
        """
        Validate operation against security context
        
        Args:
            operation: Operation details
            context: Security context
            required_level: Required permission level
            
        Returns:
            True if operation is permitted
        """
        # Check session validity
        if not self._is_valid_session(context.session_id):
            return False
            
        # Validate user permissions
        return context.validator.check_user_permission(
            context.roles,
            operation.get("type", "unknown"),
            required_level
        )

    def _is_valid_session(self, session_id: str) -> bool:
        """
        Check if a session is valid
        
        Args:
            session_id: Session ID to check
            
        Returns:
            True if session is valid
        """
        # In real implementation would check session state
        return session_id in self.sessions

    def check_user_permission(self, 
                            user_roles: List[str],
                            resource_type: str,
                            required_level: PermissionLevel) -> bool:
        """
        Check if user has sufficient permission
        
        Args:
            user_roles: User's roles
            resource_type: Type of resource
            required_level: Required permission level
            
        Returns:
            True if permitted
        """
        # In real implementation would check actual permissions
        return True

    def add_security_check(self, 
                          context: SecurityContext,
                          check_type: str,
                          details: Dict[str, Any]) -> None:
        """
        Add a security check to the context
        
        Args:
            context: Security context
            check_type: Type of check
            details: Additional details
        """
        # In real implementation would record check
        pass

    def get_context_status(self, session_id: str) -> Dict[str, Any]:
        """
        Get status of a security context
        
        Args:
            session_id: Session ID to check
            
        Returns:
            Context status information
        """
        # Would return actual context info in real implementation
        return {
            "valid": session_id in self.sessions,
            "session_id": session_id,
            "last_checked": datetime.now().isoformat()
        }

    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        # Would implement actual cleanup logic
        return 0

    def set_policy(self, policy_name: str, value: Any) -> None:
        """
        Set a security policy
        
        Args:
            policy_name: Name of policy
            value: Policy value
        """
        self.policies[policy_name] = value

    def get_policy(self, policy_name: str) -> Any:
        """
        Get a security policy value
        
        Args:
            policy_name: Name of policy
            
        Returns:
            Policy value
        """
        return self.policies.get(policy_name)