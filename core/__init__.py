"""
Core module initialization for Manus AI Clone
Exports main classes for external use
"""

# Core module initialization
from .engine import ManusAIEngine
from .message_router import MessageRouter
from .event_processor import EventProcessor

__all__ = [
    'ManusAIEngine',
    'MessageRouter',
    'EventProcessor'
]
