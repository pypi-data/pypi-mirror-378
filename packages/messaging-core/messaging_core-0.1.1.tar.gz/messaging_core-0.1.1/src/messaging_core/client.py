import grpc
import logging
from typing import Optional, List, Dict, Any, Iterator, Union, Tuple, Callable, TypeVar, Type
from datetime import datetime
import functools
from enum import Enum

# Import generated protobuf and gRPC modules
from . import auth_pb2 as auth_pb2
from . import auth_pb2_grpc as auth_pb2_grpc
from . import messaging_pb2 as msg_pb2
from . import messaging_pb2_grpc as msg_pb2_grpc
from . import conversation_pb2 as conv_pb2
from . import conversation_pb2_grpc as conv_pb2_grpc
from . import attachment_pb2 as attach_pb2
from . import attachment_pb2_grpc as attach_pb2_grpc
from . import users_pb2 as users_pb2
from . import users_pb2_grpc as users_pb2_grpc

# Import enums
from .enums import MessageType, MessageStatus

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessagingCoreClient:
    """
    A high-level client for interacting with the Messaging Core services.
    This client provides an easy-to-use interface for authentication and messaging operations.
    """
    
    def __init__(self, server_address: str, api_key: str, use_ssl: bool = True):
        """
        Initialize the MessagingCoreClient.
        
        Args:
            server_address: The server address in the format 'host:port'
            api_key: The API key for authentication
            use_ssl: Whether to use SSL/TLS for the connection
        """
        self.server_address = server_address
        self.api_key = api_key
        self.channel = None
        self.auth_stub = None
        self.msg_stub = None
        self.token = None
        self.refresh_token = None
        
        # Configure channel
        if use_ssl:
            # For production, use SSL credentials
            self.channel = grpc.secure_channel(
                server_address,
                grpc.ssl_channel_credentials()
            )
        else:
            # For development/testing without SSL
            self.channel = grpc.insecure_channel(server_address)
        
        # Initialize stubs with interceptors
        self._initialize_stubs()
    
    def _get_metadata(self) -> List[Tuple[str, str]]:
        """
        Get metadata with API key and authentication token for gRPC calls.
        
        Returns:
            List of metadata tuples (key, value)
        """
        metadata = [('x-api-key', self.api_key)]
        if self.token:
            metadata.append(('authorization', f'Bearer {self.token}'))
        return metadata
    
    def _wrap_rpc_call(self, method: Callable, request, **kwargs):
        """
        Wrapper for RPC calls to add authentication metadata.
        
        Args:
            method: The gRPC method to call
            request: The request message
            **kwargs: Additional keyword arguments
            
        Returns:
            The response from the gRPC method
        """
        metadata = self._get_metadata()
        return method(request, metadata=metadata, **kwargs)
    
    def _initialize_stubs(self):
        """Initialize the gRPC stubs."""
        self.auth_stub = auth_pb2_grpc.AuthServiceStub(self.channel)
        self.msg_stub = msg_pb2_grpc.MessagingServiceStub(self.channel)
        self.conversation_stub = conv_pb2_grpc.ConversationServiceStub(self.channel)
        self.attachment_stub = attach_pb2_grpc.AttachmentServiceStub(self.channel)
        self.users_stub = users_pb2_grpc.UserServiceStub(self.channel)
    
    # ============================================
    # Conversation Service Methods
    # ============================================

    def create_conversation(
        self,
        title: str,
        conversation_type: str = "CONVERSATION_TYPE_DIRECT",
        participant_ids: Optional[List[str]] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new conversation.
        
        Args:
            title: Title of the conversation
            conversation_type: Type of conversation (CONVERSATION_TYPE_DIRECT or CONVERSATION_TYPE_GROUP)
            participant_ids: List of user IDs to add as participants
            metadata: Optional metadata for the conversation
            
        Returns:
            dict: Result of the conversation creation
        """
        try:
            request = conv_pb2.CreateConversationRequest(
                title=title,
                type=conv_pb2.ConversationType.Value(conversation_type),
                participant_ids=participant_ids or [],
                metadata=[conv_pb2.Metadata(key=k, value=v) for k, v in (metadata or {}).items()]
            )
            response = self._wrap_rpc_call(self.conversation_stub.CreateConversation, request)
            return {
                'id': response.id,
                'success': response.success,
                'error': response.error
            }
        except grpc.RpcError as e:
            logger.error(f"Failed to create conversation: {e.details()}")
            raise

    def get_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get a conversation by ID.
        
        Args:
            conversation_id: ID of the conversation to retrieve
            
        Returns:
            dict: Conversation details
        """
        try:
            request = conv_pb2.GetConversationRequest(id=conversation_id)
            response = self._wrap_rpc_call(self.conversation_stub.GetConversation, request)
            
            if not response.success:
                return {'success': False, 'error': response.error}
                
            conv = response.conversation
            return {
                'id': conv.id,
                'title': conv.title,
                'type': conv_pb2.ConversationType.Name(conv.type),
                'participants': [{
                    'id': p.id,
                    'user_id': p.user_id,
                    'role': conv_pb2.ParticipantRole.Name(p.role)
                } for p in conv.participants],
                'created_at': conv.created_at.ToDatetime(),
                'updated_at': conv.updated_at.ToDatetime(),
                'success': True
            }
        except grpc.RpcError as e:
            logger.error(f"Failed to get conversation: {e.details()}")
            raise

    def list_conversations(self, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """
        List conversations with pagination.
        
        Args:
            page: Page number (1-based)
            page_size: Number of items per page
            
        Returns:
            dict: List of conversations and pagination info
        """
        try:
            request = conv_pb2.ListConversationsRequest(page=page, page_size=page_size)
            response = self._wrap_rpc_call(self.conversation_stub.ListConversations, request)
            
            return {
                'conversations': [{
                    'id': conv.id,
                    'title': conv.title,
                    'type': conv_pb2.ConversationType.Name(conv.type),
                    'last_message_at': conv.last_message_at.ToDatetime() if conv.HasField('last_message_at') else None,
                    'unread_count': conv.unread_count,
                    'is_muted': conv.is_muted,
                    'is_archived': conv.is_archived
                } for conv in response.conversations],
                'total_count': response.total_count,
                'success': True
            }
        except grpc.RpcError as e:
            logger.error(f"Failed to list conversations: {e.details()}")
            raise

    def add_participant(
        self,
        conversation_id: str,
        user_id: str,
        role: str = "PARTICIPANT_ROLE_MEMBER"
    ) -> Dict[str, Any]:
        """
        Add a participant to a conversation.
        
        Args:
            conversation_id: ID of the conversation
            user_id: ID of the user to add
            role: Role of the participant (default: PARTICIPANT_ROLE_MEMBER)
            
        Returns:
            dict: Result of the operation
        """
        try:
            request = conv_pb2.AddParticipantRequest(
                conversation_id=conversation_id,
                user_id=user_id,
                role=conv_pb2.ParticipantRole.Value(role)
            )
            response = self._wrap_rpc_call(self.conversation_stub.AddParticipant, request)
            return {
                'success': response.success,
                'error': response.error
            }
        except grpc.RpcError as e:
            logger.error(f"Failed to add participant: {e.details()}")
            raise

    def remove_participant(self, conversation_id: str, user_id: str) -> Dict[str, Any]:
        """
        Remove a participant from a conversation.
        
        Args:
            conversation_id: ID of the conversation
            user_id: ID of the user to remove
            
        Returns:
            dict: Result of the operation
        """
        try:
            request = conv_pb2.RemoveParticipantRequest(
                conversation_id=conversation_id,
                user_id=user_id
            )
            response = self._wrap_rpc_call(self.conversation_stub.RemoveParticipant, request)
            return {
                'success': response.success,
                'error': response.error
            }
        except grpc.RpcError as e:
            logger.error(f"Failed to remove participant: {e.details()}")
            raise
            
    def update_conversation(
        self,
        conversation_id: str,
        title: Optional[str] = None,
        conversation_type: Optional[str] = None,
        avatar_url: Optional[str] = None,
        participant_ids: Optional[List[str]] = None,
        admin_ids: Optional[List[str]] = None,
        metadata: Optional[Dict[str, str]] = None,
        is_archived: Optional[bool] = None,
        is_muted: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Update an existing conversation.
        
        Args:
            conversation_id: ID of the conversation to update
            title: New title for the conversation
            conversation_type: New type of conversation (CONVERSATION_TYPE_DIRECT or CONVERSATION_TYPE_GROUP)
            avatar_url: New avatar URL for the conversation
            participant_ids: New list of participant IDs
            admin_ids: New list of admin user IDs
            metadata: Optional metadata to update
            is_archived: Whether the conversation is archived
            is_muted: Whether the conversation is muted
            
        Returns:
            dict: Updated conversation details
        """
        try:
            request = conv_pb2.UpdateConversationRequest(id=conversation_id)
            
            if title is not None:
                request.title = title
            if conversation_type is not None:
                request.type = conv_pb2.ConversationType.Value(conversation_type)
            if avatar_url is not None:
                request.avatar_url = avatar_url
            if participant_ids is not None:
                request.participant_ids.extend(participant_ids)
            if admin_ids is not None:
                request.admin_ids.extend(admin_ids)
            if metadata is not None:
                request.metadata.extend([conv_pb2.Metadata(key=k, value=v) for k, v in metadata.items()])
            if is_archived is not None:
                request.is_archived = is_archived
            if is_muted is not None:
                request.is_muted = is_muted
                
            response = self._wrap_rpc_call(self.conversation_stub.UpdateConversation, request)
            
            if not response.success:
                return {'success': False, 'error': response.error}
                
            conv = response.conversation
            return {
                'id': conv.id,
                'title': conv.title,
                'type': conv_pb2.ConversationType.Name(conv.type),
                'is_archived': conv.is_archived,
                'is_muted': conv.is_muted,
                'success': True
            }
        except grpc.RpcError as e:
            logger.error(f"Failed to update conversation: {e.details()}")
            raise
            
    def delete_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """
        Delete a conversation.
        
        Args:
            conversation_id: ID of the conversation to delete
            
        Returns:
            dict: Result of the delete operation
        """
        try:
            request = conv_pb2.DeleteConversationRequest(id=conversation_id)
            response = self._wrap_rpc_call(self.conversation_stub.DeleteConversation, request)
            return {
                'success': response.success,
                'error': response.error
            }
        except grpc.RpcError as e:
            logger.error(f"Failed to delete conversation: {e.details()}")
            raise
            
    def update_participant(
        self,
        participant_id: str,
        role: Optional[str] = None,
        is_muted: Optional[bool] = None,
        nickname: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Update a participant's information in a conversation.
        
        Args:
            participant_id: ID of the participant to update
            role: New role for the participant (PARTICIPANT_ROLE_MEMBER or PARTICIPANT_ROLE_ADMIN)
            is_muted: Whether the participant is muted
            nickname: New nickname for the participant
            metadata: Optional metadata to update
            
        Returns:
            dict: Updated participant information
        """
        try:
            # First get the current participant
            request = conv_pb2.UpdateParticipantRequest(id=participant_id)
            
            # Create a new participant with updated fields
            participant = conv_pb2.Participant(id=participant_id)
            
            if role is not None:
                participant.role = conv_pb2.ParticipantRole.Value(role)
            if is_muted is not None:
                participant.is_muted = is_muted
            if nickname is not None:
                participant.nickname = nickname
            if metadata is not None:
                participant.metadata.extend([conv_pb2.Metadata(key=k, value=v) for k, v in metadata.items()])
                
            request.participant.CopyFrom(participant)
            
            response = self._wrap_rpc_call(self.conversation_stub.UpdateParticipant, request)
            
            # The response is the updated participant
            p = response.participant
            return {
                'id': p.id,
                'conversation_id': p.conversation_id,
                'user_id': p.user_id,
                'role': conv_pb2.ParticipantRole.Name(p.role),
                'is_muted': p.is_muted,
                'nickname': p.nickname,
                'success': True
            }
        except grpc.RpcError as e:
            logger.error(f"Failed to update participant: {e.details()}")
            raise
            
    def list_participants(
        self,
        conversation_id: str,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """
        List all participants in a conversation.
        
        Args:
            conversation_id: ID of the conversation
            page: Page number (1-based)
            page_size: Number of items per page
            
        Returns:
            dict: List of participants and pagination info
        """
        try:
            request = conv_pb2.ListParticipantsRequest(
                conversation_id=conversation_id,
                page=page,
                page_size=page_size
            )
            response = self._wrap_rpc_call(self.conversation_stub.ListParticipants, request)
            
            return {
                'participants': [{
                    'id': p.id,
                    'user_id': p.user_id,
                    'role': conv_pb2.ParticipantRole.Name(p.role),
                    'is_admin': p.is_admin,
                    'is_muted': p.is_muted,
                    'nickname': p.nickname,
                    'joined_at': p.joined_at.ToDatetime(),
                    'left_at': p.left_at.ToDatetime() if p.HasField('left_at') else None
                } for p in response.participants],
                'total_count': response.TotalCount,
                'success': True
            }
        except grpc.RpcError as e:
            logger.error(f"Failed to list participants: {e.details()}")
            raise
            
    def get_conversation_settings(
        self,
        conversation_id: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get conversation settings for a user.
        
        Args:
            conversation_id: ID of the conversation
            user_id: ID of the user (defaults to current user if None)
            
        Returns:
            dict: Conversation settings
        """
        try:
            if user_id is None and not self.token:
                raise ValueError("User ID is required when not authenticated")
                
            request = conv_pb2.GetConversationSettingsRequest(
                conversation_id=conversation_id,
                user_id=user_id if user_id else ''  # Server will use current user if empty
            )
            
            response = self._wrap_rpc_call(self.conversation_stub.GetConversationSettings, request)
            
            settings = response.settings
            return {
                'id': settings.id,
                'conversation_id': settings.conversation_id,
                'user_id': settings.user_id,
                'is_muted': settings.is_muted,
                'is_archived': settings.is_archived,
                'custom_name': settings.custom_name,
                'metadata': {m.key: m.value for m in settings.metadata},
                'created_at': settings.created_at.ToDatetime(),
                'updated_at': settings.updated_at.ToDatetime(),
                'success': True
            }
        except grpc.RpcError as e:
            logger.error(f"Failed to get conversation settings: {e.details()}")
            raise
            
    def update_conversation_settings(
        self,
        conversation_id: str,
        is_muted: Optional[bool] = None,
        is_archived: Optional[bool] = None,
        custom_name: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update conversation settings for a user.
        
        Args:
            conversation_id: ID of the conversation
            is_muted: Whether the conversation is muted
            is_archived: Whether the conversation is archived
            custom_name: Custom name for the conversation
            metadata: Optional metadata to update
            user_id: ID of the user (defaults to current user if None)
            
        Returns:
            dict: Updated conversation settings
        """
        try:
            if user_id is None and not self.token:
                raise ValueError("User ID is required when not authenticated")
                
            # First get current settings
            get_request = conv_pb2.GetConversationSettingsRequest(
                conversation_id=conversation_id,
                user_id=user_id if user_id else ''
            )
            get_response = self._wrap_rpc_call(self.conversation_stub.GetConversationSettings, get_request)
            
            # Update fields that were provided
            settings = get_response.settings
            if is_muted is not None:
                settings.is_muted = is_muted
            if is_archived is not None:
                settings.is_archived = is_archived
            if custom_name is not None:
                settings.custom_name = custom_name
            if metadata is not None:
                settings.metadata.extend([conv_pb2.Metadata(key=k, value=v) for k, v in metadata.items()])
            
            # Update the settings
            update_request = conv_pb2.UpdateConversationSettingsRequest(
                conversation_id=conversation_id,
                user_id=user_id if user_id else '',
                settings=settings
            )
            
            update_response = self._wrap_rpc_call(
                self.conversation_stub.UpdateConversationSettings, 
                update_request
            )
            
            updated = update_response.settings
            return {
                'id': updated.id,
                'conversation_id': updated.conversation_id,
                'user_id': updated.user_id,
                'is_muted': updated.is_muted,
                'is_archived': updated.is_archived,
                'custom_name': updated.custom_name,
                'metadata': {m.key: m.value for m in updated.metadata},
                'success': True
            }
        except grpc.RpcError as e:
            logger.error(f"Failed to update conversation settings: {e.details()}")
            raise

    # ============================================
    # Attachment Service Methods
    # ============================================

    def upload_file(
        self,
        file_path: str,
        content_type: str = "application/octet-stream",
        metadata: Optional[Dict[str, str]] = None,
        chunk_size: int = 1024 * 1024  # 1MB chunks
    ) -> Dict[str, Any]:
        """
        Upload a file to the attachment service.
        
        Args:
            file_path: Path to the file to upload
            content_type: MIME type of the file
            metadata: Optional metadata for the file
            chunk_size: Size of each chunk in bytes
            
        Returns:
            dict: Upload result with file ID and URL
        """
        try:
            import os
            import mimetypes
            
            # Get file info
            file_size = os.path.getsize(file_path)
            file_name = os.path.basename(file_path)
            
            # If content type is not provided, try to guess it
            if content_type == "application/octet-stream":
                content_type, _ = mimetypes.guess_type(file_path) or (content_type, None)
            
            # Create metadata
            metadata = metadata or {}
            
            def file_chunks():
                # First yield the file info
                yield attach_pb2.UploadFileRequest(
                    info=attach_pb2.FileInfo(
                        filename=file_name,
                        content_type=content_type,
                        size=file_size,
                        metadata=metadata
                    )
                )
                
                # Then yield file chunks
                with open(file_path, 'rb') as f:
                    while True:
                        chunk = f.read(chunk_size)
                        if not chunk:
                            break
                        yield attach_pb2.UploadFileRequest(chunk_data=chunk)
            
            # Make the streaming RPC call
            response = self.attachment_stub.UploadFile(
                file_chunks(),
                metadata=self._get_metadata()
            )
            
            return {
                'id': response.id,
                'url': response.url,
                'size': response.size,
                'message': response.message,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Failed to upload file: {str(e)}")
            raise

    def download_file(self, file_id: str, save_path: str) -> Dict[str, Any]:
        """
        Download a file from the attachment service.
        
        Args:
            file_id: ID of the file to download
            save_path: Path where to save the downloaded file
            
        Returns:
            dict: Download result with file info
        """
        try:
            request = attach_pb2.DownloadFileRequest(id=file_id)
            response_stream = self.attachment_stub.DownloadFile(
                request,
                metadata=self._get_metadata()
            )
            
            file_info = None
            with open(save_path, 'wb') as f:
                for response in response_stream:
                    if response.HasField('info'):
                        file_info = response.info
                    elif response.HasField('chunk_data'):
                        f.write(response.chunk_data)
            
            if not file_info:
                raise ValueError("No file info received in response")
                
            return {
                'id': file_info.id,
                'filename': file_info.filename,
                'size': file_info.size,
                'content_type': file_info.content_type,
                'saved_to': save_path,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Failed to download file: {str(e)}")
            raise

    def delete_file(self, file_id: str) -> Dict[str, Any]:
        """
        Delete a file from the attachment service.
        
        Args:
            file_id: ID of the file to delete
            
        Returns:
            dict: Result of the delete operation
        """
        try:
            request = attach_pb2.DeleteFileRequest(id=file_id)
            response = self._wrap_rpc_call(self.attachment_stub.DeleteFile, request)
            
            return {
                'success': response.success,
                'message': response.message
            }
            
        except grpc.RpcError as e:
            logger.error(f"Failed to delete file: {e.details()}")
            raise

    def get_file_info(self, file_id: str) -> Dict[str, Any]:
        """
        Get information about a file.
        
        Args:
            file_id: ID of the file
            
        Returns:
            dict: File information
        """
        try:
            request = attach_pb2.GetFileInfoRequest(id=file_id)
            response = self._wrap_rpc_call(self.attachment_stub.GetFileInfo, request)
            
            if not response.exists:
                return {'exists': False, 'success': True}
                
            file_info = response.file_info
            return {
                'id': file_info.id,
                'filename': file_info.filename,
                'content_type': file_info.content_type,
                'size': file_info.size,
                'created_at': file_info.created_at.ToDatetime(),
                'metadata': dict(file_info.metadata),
                'exists': True,
                'success': True
            }
            
        except grpc.RpcError as e:
            logger.error(f"Failed to get file info: {e.details()}")
            raise

    def generate_presigned_url(self, file_id: str, expires: int = 3600) -> Dict[str, Any]:
        """
        Generate a presigned URL for a file.
        
        Args:
            file_id: ID of the file
            expires: Expiration time in seconds (default: 1 hour)
            
        Returns:
            dict: Presigned URL and expiration info
        """
        try:
            request = attach_pb2.GeneratePresignedURLRequest(
                id=file_id,
                expires=expires
            )
            response = self._wrap_rpc_call(
                self.attachment_stub.GeneratePresignedURL,
                request
            )
            
            return {
                'url': response.url,
                'expires_in': expires,
                'success': True
            }
            
        except grpc.RpcError as e:
            logger.error(f"Failed to generate presigned URL: {e.details()}")
            raise

    def close(self):
        """Close the gRPC channel."""
        if self.channel:
            self.channel.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    # ============================================
    # User Service Methods
    # ============================================
    
    def add_user(
        self,
        username: str,
        email: str,
        phone_number: str,
        firstname: str,
        lastname: str
    ) -> Dict[str, Any]:
        """
        Add a new user to the system.
        
        Args:
            username: Unique username for the user
            email: User's email address
            phone_number: User's phone number
            firstname: User's first name
            lastname: User's last name
            
        Returns:
            dict: Result of the user creation
        """
        try:
            request = users_pb2.AddUserRequest(
                username=username,
                email=email,
                phoneNumber=phone_number,
                firstname=firstname,
                lastname=lastname
            )
            
            response = self._wrap_rpc_call(self.users_stub.AddUser, request)
            
            return {
                'user_id': response.user_id,
                'success': response.success,
                'error': response.error,
                'server_timestamp': response.server_timestamp.ToDatetime()
            }
            
        except grpc.RpcError as e:
            logger.error(f"Failed to add user: {e.details()}")
            raise
    
    def get_user(self, user_id: str) -> Dict[str, Any]:
        """
        Get user information by ID.
        
        Args:
            user_id: ID of the user to retrieve
            
        Returns:
            dict: User information
        """
        try:
            request = users_pb2.GetUserRequest(user_id=user_id)
            response = self._wrap_rpc_call(self.users_stub.GetUser, request)
            
            return {
                'user_id': response.user_id,
                'username': response.username,
                'email': response.email,
                'phone_number': response.phone_number,
                'first_name': response.first_name,
                'last_name': response.last_name,
                'display_name': response.display_name,
                'avatar_url': response.avatar_url,
                'bio': response.bio,
                'status': response.status,
                'last_seen_at': response.last_seen_at.ToDatetime() if response.HasField('last_seen_at') else None,
                'is_online': response.is_online,
                'is_verified': response.is_verified,
                'is_bot': response.is_bot,
                'language': response.language,
                'time_zone': response.time_zone,
                'created_at': response.created_at.ToDatetime(),
                'updated_at': response.updated_at.ToDatetime(),
                'success': True
            }
            
        except grpc.RpcError as e:
            logger.error(f"Failed to get user: {e.details()}")
            raise
    
    # ============================================
    # Authentication Methods
    
    def login(self, email: str, password: str) -> dict:
        """
        Authenticate a user with email and password.
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            dict: Authentication tokens and user information
            
        Raises:
            grpc.RpcError: If the login request fails
        """
        try:
            request = auth_pb2.LoginRequest(email=email, password=password)
            # Use the wrapper to include API key in metadata
            response = self._wrap_rpc_call(self.auth_stub.Login, request)
            
            # Store tokens for future requests
            self.token = response.token
            self.refresh_token = response.refresh_token
            
            return {
                'token': response.token,
                'refresh_token': response.refresh_token,
                'expires_in': response.expires_in
            }
        except grpc.RpcError as e:
            logger.error(f"Login failed: {e.details()}")
            raise
    
    def register(self, email: str, password: str, full_name: str) -> dict:
        """
        Register a new user account.
        
        Args:
            email: User's email address
            password: User's password
            full_name: User's full name
            
        Returns:
            dict: Registration result
            
        Raises:
            grpc.RpcError: If the registration request fails
        """
        try:
            request = auth_pb2.RegisterRequest(
                email=email,
                password=password,
                full_name=full_name
            )
            response = self._wrap_rpc_call(self.auth_stub.Register, request)
            
            return {
                'user_id': response.user_id,
                'success': response.success,
                'target_url': response.targetUrl,
                'error': response.error
            }
        except grpc.RpcError as e:
            logger.error(f"Registration failed: {e.details()}")
            raise
    
    def refresh_token(self) -> dict:
        """
        Refresh the authentication token using the refresh token.
        
        Returns:
            dict: New tokens and expiration information
            
        Raises:
            ValueError: If no token or refresh token is available
            grpc.RpcError: If the token refresh fails
        """
        if not self.token or not self.refresh_token:
            raise ValueError("No token or refresh token available")
            
        try:
            request = auth_pb2.RefreshTokenRequest(
                token=self.token,
                refresh_token=self.refresh_token
            )
            response = self._wrap_rpc_call(self.auth_stub.RefreshToken, request)
            
            # Update stored tokens
            self.token = response.token
            self.refresh_token = response.refresh_token
            
            return {
                'token': response.token,
                'refresh_token': response.refresh_token,
                'expires_in': response.expires_in
            }
        except grpc.RpcError as e:
            logger.error(f"Token refresh failed: {e.details()}")
            raise
    
    # Messaging Methods
    
    def send_message(
        self,
        conversation_id: str,
        text: str = "",
        message_type: Union[str, MessageType] = MessageType.TEXT,
        media_info: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        properties: Optional[Dict[str, str]] = None
    ) -> dict:
        """
        Send a message to a conversation.
        
        Args:
            conversation_id: ID of the conversation
            text: Message text content
            message_type: Type of message. Must be one of: 'TEXT', 'IMAGE', 'VIDEO', 'FILE', 'AUDIO'.
                        These correspond to the MessageType enum in the protobuf definition.
            media_info: Dictionary containing media information (required for non-text message types).
                       Should include: file_name, mime_type, file_size, url, caption, metadata.
            headers: Optional message headers as key-value pairs
            properties: Optional message properties as key-value pairs
            
        Returns:
            dict: A dictionary containing:
                - message_id: ID of the sent message
                - success: Boolean indicating if the operation was successful
                - error: Error message if the operation failed
                - server_timestamp: When the message was received by the server
                - status: Current status of the message (e.g., 'SENT', 'DELIVERED')
            
        Raises:
            grpc.RpcError: If the message sending fails
            ValueError: If an invalid message_type is provided
        """
        try:
            # Convert to gRPC enum value
            if isinstance(message_type, str):
                message_type = MessageType(message_type)
            grpc_message_type = MessageType.to_grpc_enum(message_type)
                
            # Prepare the request
            request = msg_pb2.SendMessageRequest(
                conversation_id=conversation_id,
                text=text,
                message_type=grpc_message_type
            )
            
            # Add headers if provided
            if headers:
                for key, value in headers.items():
                    request.headers.append(
                        msg_pb2.Header(key=key, value=str(value))
                    )
            
            # Add media info if not a text message
            if media_info and message_type != MessageType.TEXT:
                request.media_info.CopyFrom(
                    msg_pb2.MediaInfo(
                        file_name=media_info.get('file_name', ''),
                        mime_type=media_info.get('mime_type', ''),
                        file_size=media_info.get('file_size', 0),
                        url=media_info.get('url', ''),
                        caption=media_info.get('caption', ''),
                        metadata=media_info.get('metadata', {})
                    )
                )
            
            # Add properties if provided
            if properties:
                for key, value in properties.items():
                    request.properties[key] = str(value)
            
            # Set the client timestamp
            request.timestamp.FromDatetime(datetime.utcnow())
            
            # Send the message with authentication
            response = self._wrap_rpc_call(self.msg_stub.SendMessage, request)
            
            return {
                'message_id': response.message_id,
                'success': response.success,
                'error': response.error,
                'server_timestamp': response.server_timestamp.ToDatetime(),
                'status': MessageStatus.from_grpc_enum(response.status).value
            }
            
        except grpc.RpcError as e:
            logger.error(f"Failed to send message: {e.details()}")
            raise
    
    def get_conversation_messages(
        self,
        conversation_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[dict]:
        """
        Retrieve messages from a conversation.
        
        Args:
            conversation_id: ID of the conversation
            limit: Maximum number of messages to retrieve
            offset: Pagination offset
            
        Returns:
            List[dict]: List of message dictionaries
            
        Raises:
            grpc.RpcError: If the request fails
        """
        try:
            request = msg_pb2.GetConversationMessagesRequest(
                conversation_id=conversation_id,
                limit=limit,
                offset=offset
            )
            
            response = self._wrap_rpc_call(self.msg_stub.GetConversationMessages, request)
            
            messages = []
            for msg in response.messages:
                message_dict = {
                    'id': msg.id,
                    'conversation_id': msg.conversation_id,
                    'sender': msg.sender,
                    'message_type': msg_pb2.MessageType.Name(msg.message_type),
                    'text_content': msg.text_content,
                    'status': msg_pb2.MessageStatus.Name(msg.status),
                    'created_at': msg.created_at.ToDatetime(),
                    'headers': {h.key: h.value for h in msg.headers},
                    'properties': dict(msg.properties)
                }
                
                if msg.HasField('media_info'):
                    message_dict['media_info'] = {
                        'file_name': msg.media_info.file_name,
                        'mime_type': msg.media_info.mime_type,
                        'file_size': msg.media_info.file_size,
                        'url': msg.media_info.url,
                        'caption': msg.media_info.caption,
                        'metadata': dict(msg.media_info.metadata)
                    }
                
                messages.append(message_dict)
            
            return messages
            
        except grpc.RpcError as e:
            logger.error(f"Failed to get conversation messages: {e.details()}")
            raise
    
    def subscribe_messages(self) -> Iterator[dict]:
        """
        Subscribe to real-time message updates.
        
        Yields:
            dict: Message or status update
            
        Raises:
            grpc.RpcError: If the subscription fails
        """
        try:
            request = msg_pb2.SubscribeMessagesRequest()
            
            # For streaming calls, we need to pass metadata to the initial request
            metadata = self._get_metadata()
            for response in self.msg_stub.SubscribeMessages(request, metadata=metadata):
                if response.HasField('message'):
                    msg = response.message
                    yield {
                        'type': 'message',
                        'data': {
                            'id': msg.id,
                            'conversation_id': msg.conversation_id,
                            'sender': msg.sender,
                            'message_type': msg_pb2.MessageType.Name(msg.message_type),
                            'text_content': msg.text_content,
                            'created_at': msg.created_at.ToDatetime(),
                            'status': msg_pb2.MessageStatus.Name(msg.status)
                        }
                    }
                elif response.HasField('status_updated'):
                    status = response.status_updated
                    yield {
                        'type': 'status_update',
                        'data': {
                            'message_id': status.message_id,
                            'status': msg_pb2.MessageStatus.Name(status.status)
                        }
                    }
                elif response.HasField('user_status_update'):
                    update = response.user_status_update
                    yield {
                        'type': 'user_status',
                        'data': {
                            'user_id': update.user_id,
                            'status': msg_pb2.UserStatus.Name(update.status),
                            'timestamp': update.timestamp.ToDatetime()
                        }
                    }
                    
        except grpc.RpcError as e:
            logger.error(f"Subscription error: {e.details()}")
            raise
    
    def update_message_status(
        self,
        message_id: str,
        status: str
    ) -> dict:
        """
        Update the status of a message.
        
        Args:
            message_id: ID of the message to update
            status: New status (SENT, DELIVERED, SEEN, FAILED)
            
        Returns:
            dict: Update result
            
        Raises:
            grpc.RpcError: If the update fails
        """
        try:
            request = msg_pb2.UpdateMessageStatusRequest(
                message_id=message_id,
                status=msg_pb2.MessageStatus.Value(status),
                status_timestamp=datetime.utcnow()
            )
            
            response = self._wrap_rpc_call(self.msg_stub.UpdateMessageStatus, request)
            
            return {
                'success': response.success,
                'error': response.error,
                'new_status': msg_pb2.MessageStatus.Name(response.new_status),
                'server_timestamp': response.server_timestamp.ToDatetime()
            }
            
        except grpc.RpcError as e:
            logger.error(f"Failed to update message status: {e.details()}")
            raise
    
    def bulk_update_message_status(
        self,
        message_ids: List[str],
        conversation_id: str,
        status: str
    ) -> dict:
        """
        Update the status of multiple messages at once.
        
        Args:
            message_ids: List of message IDs to update
            conversation_id: ID of the conversation
            status: New status (SENT, DELIVERED, SEEN, FAILED)
            
        Returns:
            dict: Bulk update result
            
        Raises:
            grpc.RpcError: If the bulk update fails
        """
        try:
            request = msg_pb2.BulkUpdateMessageStatusRequest(
                message_ids=message_ids,
                conversation_id=conversation_id,
                status=msg_pb2.MessageStatus.Value(status)
            )
            
            response = self._wrap_rpc_call(self.msg_stub.BulkUpdateMessageStatus, request)
            
            return {
                'success': response.success,
                'error': response.error,
                'updated_count': response.updated_count,
                'server_timestamp': response.server_timestamp.ToDatetime()
            }
            
        except grpc.RpcError as e:
            logger.error(f"Bulk update message status failed: {e.details()}")
            raise
