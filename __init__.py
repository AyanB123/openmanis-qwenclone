"""
Manus AI Clone Core Module
Implements the main components of the Manus AI system
"""

# Import core components
from .core.engine import ManusAIEngine
from .core.message_router import MessageRouter
from .core.event_processor import EventProcessor

# Import planner components
from .planner.task_planner import TaskPlanner

# Import security components
from .security.permission_validator import PermissionValidator
from .security.role_permissions import RoleManager
from .security.access_rule_manager import AccessRuleManager
from .security.audit_logger import AuditLogger

# Import tool components
from .tools.tool_interface import ToolAdapter
from .tools.message_tool import MessageTool
from .tools.file_tool import FileTool
from .tools.shell_tool import ShellTool
from .tools.browser_tool import BrowserTool
from .tools.knowledge_tool import KnowledgeTool

# Import system integration components
from .system_integration.component_connector import ComponentConnector

__all__ = [
    # Core components
    'ManusAIEngine',
    'MessageRouter',
    'EventProcessor',
    
    # Planner components
    'TaskPlanner',
    
    # Security components
    'PermissionValidator',
    'RoleManager',
    'AccessRuleManager',
    'AuditLogger',
    
    # Tool components
    'ToolAdapter',
    'MessageTool',
    'FileTool',
    'ShellTool',
    'BrowserTool',
    'KnowledgeTool',
    
    # System integration components
    'ComponentConnector'
]