"""Repository interfaces for dependency inversion"""
from abc import ABC, abstractmethod
from typing import List, Optional
from src.core.models.character import Character
from src.core.models.session import Session
from src.core.models.message import Message


class ICharacterRepository(ABC):
    """Interface for character repository"""
    
    @abstractmethod
    async def get_by_id(self, character_id: str) -> Optional[Character]:
        """Get character by ID"""
        pass
    
    @abstractmethod
    async def get_all(self) -> List[Character]:
        """Get all characters"""
        pass
    
    @abstractmethod
    async def create(self, character: Character) -> bool:
        """Create a new character"""
        pass
    
    @abstractmethod
    async def update(self, character: Character) -> bool:
        """Update existing character"""
        pass
    
    @abstractmethod
    async def delete(self, character_id: str) -> bool:
        """Delete character by ID"""
        pass


class ISessionRepository(ABC):
    """Interface for session repository"""
    
    @abstractmethod
    async def get_by_id(self, session_id: str) -> Optional[Session]:
        """Get session by ID"""
        pass
    
    @abstractmethod
    async def get_by_character(self, character_id: str) -> Optional[Session]:
        """Get session by character ID"""
        pass
    
    @abstractmethod
    async def get_all(self) -> List[Session]:
        """Get all sessions"""
        pass
    
    @abstractmethod
    async def create(self, session: Session) -> bool:
        """Create a new session"""
        pass
    
    @abstractmethod
    async def update(self, session: Session) -> bool:
        """Update existing session"""
        pass
    
    @abstractmethod
    async def delete(self, session_id: str) -> bool:
        """Delete session by ID"""
        pass
    
    @abstractmethod
    async def set_active_session(self, session_id: str) -> bool:
        """Set active session"""
        pass


class IMessageRepository(ABC):
    """Interface for message repository"""
    
    @abstractmethod
    async def get_by_id(self, message_id: str) -> Optional[Message]:
        """Get message by ID"""
        pass
    
    @abstractmethod
    async def get_by_session(
        self, session_id: str, after_timestamp: Optional[float] = None
    ) -> List[Message]:
        """Get messages for a session"""
        pass
    
    @abstractmethod
    async def create(self, message: Message) -> bool:
        """Create a new message"""
        pass
    
    @abstractmethod
    async def update_recalled_status(self, message_id: str, is_recalled: bool) -> bool:
        """Update recalled status of a message"""
        pass
    
    @abstractmethod
    async def update_read_status_until(
        self, session_id: str, until_timestamp: float, is_read: bool
    ) -> bool:
        """Update read status of messages until a timestamp"""
        pass
    
    @abstractmethod
    async def delete_by_session(self, session_id: str) -> bool:
        """Delete all messages for a session"""
        pass
    
    @abstractmethod
    async def get_last_read_timestamp(self, session_id: str) -> float:
        """Get the last read timestamp for a session"""
        pass


class IConfigRepository(ABC):
    """Interface for configuration repository"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[str]:
        """Get configuration value by key"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: str) -> bool:
        """Set configuration value"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete configuration by key"""
        pass
