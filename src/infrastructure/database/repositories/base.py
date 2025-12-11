from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List

T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    def __init__(self, connection_manager):
        self.conn_mgr = connection_manager

    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[T]:
        pass

    @abstractmethod
    async def get_all(self) -> List[T]:
        pass

    @abstractmethod
    async def create(self, entity: T) -> bool:
        pass

    @abstractmethod
    async def update(self, entity: T) -> bool:
        pass

    @abstractmethod
    async def delete(self, id: str) -> bool:
        pass
