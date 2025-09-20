"""
Messaging Core SDK for Python.

This SDK provides a high-level interface for interacting with the Messaging Core service.
"""

from .client import MessagingCoreClient
from .enums import MessageType, MessageStatus

__all__ = [
    'MessagingCoreClient',
    'MessageType',
    'MessageStatus',
]