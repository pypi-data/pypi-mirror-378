"""
Enums module provides user-friendly enumerations that map to the underlying gRPC enums.
These enums provide better IDE support and type safety when using the SDK.
"""
from enum import Enum
from typing import Type, TypeVar, Dict, Any

# Type variable for generic enum type
T = TypeVar('T', bound=Enum)

class MessageType(Enum):
    """
    Enum representing different types of messages that can be sent or received.
    This maps to the MessageType enum in the protobuf definition.
    
    Attributes:
        TEXT: Text message
        IMAGE: Image message
        VIDEO: Video message
        FILE: Generic file message
        AUDIO: Audio message
    """
    TEXT = "TEXT"
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    FILE = "FILE"
    AUDIO = "AUDIO"

    @classmethod
    def to_grpc_enum(cls, value: 'MessageType') -> int:
        """
        Convert MessageType enum to the corresponding gRPC enum value.
        
        Args:
            value: The MessageType enum value to convert
            
        Returns:
            int: The corresponding gRPC enum value
            
        Raises:
            ValueError: If the value is not a valid MessageType
        """
        from . import messaging_pb2  # Import here to avoid circular imports
        
        # Map our enum values to gRPC enum values
        grpc_enum_map = {
            cls.TEXT: messaging_pb2.MessageType.TEXT,
            cls.IMAGE: messaging_pb2.MessageType.IMAGE,
            cls.VIDEO: messaging_pb2.MessageType.VIDEO,
            cls.FILE: messaging_pb2.MessageType.FILE,
            cls.AUDIO: messaging_pb2.MessageType.AUDIO,
        }
        
        if value not in grpc_enum_map:
            raise ValueError(f"Invalid MessageType: {value}")
            
        return grpc_enum_map[value]

    @classmethod
    def from_grpc_enum(cls, grpc_value: int) -> 'MessageType':
        """
        Convert from gRPC enum value to MessageType enum.
        
        Args:
            grpc_value: The gRPC enum value to convert
            
        Returns:
            MessageType: The corresponding MessageType enum value
            
        Raises:
            ValueError: If the gRPC value doesn't match any known MessageType
        """
        from . import messaging_pb2  # Import here to avoid circular imports
        
        # Map gRPC enum values to our enum values
        enum_map = {
            messaging_pb2.MessageType.TEXT: cls.TEXT,
            messaging_pb2.MessageType.IMAGE: cls.IMAGE,
            messaging_pb2.MessageType.VIDEO: cls.VIDEO,
            messaging_pb2.MessageType.FILE: cls.FILE,
            messaging_pb2.MessageType.AUDIO: cls.AUDIO,
        }
        
        if grpc_value not in enum_map:
            raise ValueError(f"Unknown gRPC MessageType value: {grpc_value}")
            
        return enum_map[grpc_value]


class MessageStatus(Enum):
    """
    Enum representing the status of a message.
    This maps to the MessageStatus enum in the protobuf definition.
    
    Attributes:
        SENT: Message has been sent
        DELIVERED: Message has been delivered to the recipient
        SEEN: Message has been seen by the recipient
        FAILED: Message delivery failed
    """
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    SEEN = "SEEN"
    FAILED = "FAILED"

    @classmethod
    def to_grpc_enum(cls, value: 'MessageStatus') -> int:
        """Convert MessageStatus enum to the corresponding gRPC enum value."""
        from . import messaging_pb2  # Import here to avoid circular imports
        
        grpc_enum_map = {
            cls.SENT: messaging_pb2.MessageStatus.SENT,
            cls.DELIVERED: messaging_pb2.MessageStatus.DELIVERED,
            cls.SEEN: messaging_pb2.MessageStatus.SEEN,
            cls.FAILED: messaging_pb2.MessageStatus.FAILED,
        }
        
        if value not in grpc_enum_map:
            raise ValueError(f"Invalid MessageStatus: {value}")
            
        return grpc_enum_map[value]

    @classmethod
    def from_grpc_enum(cls, grpc_value: int) -> 'MessageStatus':
        """Convert from gRPC enum value to MessageStatus enum."""
        from . import messaging_pb2  # Import here to avoid circular imports
        
        enum_map = {
            messaging_pb2.MessageStatus.SENT: cls.SENT,
            messaging_pb2.MessageStatus.DELIVERED: cls.DELIVERED,
            messaging_pb2.MessageStatus.SEEN: cls.SEEN,
            messaging_pb2.MessageStatus.FAILED: cls.FAILED,
        }
        
        if grpc_value not in enum_map:
            raise ValueError(f"Unknown gRPC MessageStatus value: {grpc_value}")
            
        return enum_map[grpc_value]
