import logging
from typing import List, Optional
from datetime import datetime
from src.core.models.session import Session
from src.core.interfaces.repositories import ISessionRepository
from src.infrastructure.database.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class SessionRepository(BaseRepository[Session], ISessionRepository):
    async def get_by_id(self, id: str) -> Optional[Session]:
        try:
            with self.conn_mgr.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM sessions WHERE id = ?", (id,))
                row = cursor.fetchone()
                if row:
                    return self._row_to_session(row)
                return None
        except Exception as e:
            logger.error(f"Error getting session by id: {e}", exc_info=True)
            return None

    async def get_all(self) -> List[Session]:
        try:
            with self.conn_mgr.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM sessions ORDER BY created_at ASC")
                rows = cursor.fetchall()
                return [self._row_to_session(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting all sessions: {e}", exc_info=True)
            return []

    async def create(self, session: Session) -> bool:
        try:
            with self.conn_mgr.transaction() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO sessions (id, character_id, is_active)
                    VALUES (?, ?, ?)
                """, (session.id, session.character_id, session.is_active))
                return True
        except Exception as e:
            logger.error(f"Error creating session: {e}", exc_info=True)
            return False

    async def update(self, session: Session) -> bool:
        try:
            with self.conn_mgr.transaction() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE sessions SET
                        character_id = ?, is_active = ?
                    WHERE id = ?
                """, (session.character_id, session.is_active, session.id))
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating session: {e}", exc_info=True)
            return False

    async def delete(self, id: str) -> bool:
        try:
            with self.conn_mgr.transaction() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM sessions WHERE id = ?", (id,))
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting session: {e}", exc_info=True)
            return False

    async def get_by_character(self, character_id: str) -> Optional[Session]:
        try:
            with self.conn_mgr.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM sessions WHERE character_id = ?", (character_id,))
                row = cursor.fetchone()
                if row:
                    return self._row_to_session(row)
                return None
        except Exception as e:
            logger.error(f"Error getting session by character: {e}", exc_info=True)
            return None

    async def get_active_session(self) -> Optional[Session]:
        try:
            with self.conn_mgr.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM sessions WHERE is_active = TRUE LIMIT 1")
                row = cursor.fetchone()
                if row:
                    return self._row_to_session(row)
                return None
        except Exception as e:
            logger.error(f"Error getting active session: {e}", exc_info=True)
            return None

    async def set_active_session(self, session_id: str) -> bool:
        try:
            with self.conn_mgr.transaction() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE sessions SET is_active = FALSE")
                cursor.execute("UPDATE sessions SET is_active = TRUE WHERE id = ?", (session_id,))
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error setting active session: {e}", exc_info=True)
            return False

    def _row_to_session(self, row) -> Session:
        return Session(
            id=row['id'],
            character_id=row['character_id'],
            is_active=bool(row['is_active']),
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
        )
