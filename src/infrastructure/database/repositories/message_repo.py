import json
import logging
from typing import List, Optional
from src.core.models.message import Message, MessageType
from src.core.interfaces.repositories import IMessageRepository
from src.infrastructure.database.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class MessageRepository(BaseRepository[Message], IMessageRepository):
    async def get_by_id(self, id: str) -> Optional[Message]:
        try:
            with self.conn_mgr.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM messages WHERE id = ?", (id,))
                row = cursor.fetchone()
                if row:
                    return self._row_to_message(row)
                return None
        except Exception as e:
            logger.error(f"Error getting message by id: {e}", exc_info=True)
            return None

    async def get_all(self) -> List[Message]:
        try:
            with self.conn_mgr.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM messages ORDER BY timestamp ASC")
                rows = cursor.fetchall()
                return [self._row_to_message(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting all messages: {e}", exc_info=True)
            return []

    async def create(self, message: Message) -> bool:
        try:
            with self.conn_mgr.transaction() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO messages (
                        id, session_id, sender_id, type, content,
                        metadata, is_recalled, is_read, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    message.id,
                    message.session_id,
                    message.sender_id,
                    message.type,
                    message.content,
                    json.dumps(message.metadata),
                    message.is_recalled,
                    message.is_read,
                    message.timestamp
                ))
                return True
        except Exception as e:
            logger.error(f"Error creating message: {e}", exc_info=True)
            return False

    async def update(self, message: Message) -> bool:
        try:
            with self.conn_mgr.transaction() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE messages SET
                        session_id = ?, sender_id = ?, type = ?, content = ?,
                        metadata = ?, is_recalled = ?, is_read = ?, timestamp = ?
                    WHERE id = ?
                """, (
                    message.session_id, message.sender_id, message.type, message.content,
                    json.dumps(message.metadata), message.is_recalled, message.is_read,
                    message.timestamp, message.id
                ))
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating message: {e}", exc_info=True)
            return False

    async def delete(self, id: str) -> bool:
        try:
            with self.conn_mgr.transaction() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM messages WHERE id = ?", (id,))
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting message: {e}", exc_info=True)
            return False

    async def get_by_session(
        self,
        session_id: str,
        after_timestamp: Optional[float] = None,
        limit: Optional[int] = None
    ) -> List[Message]:
        try:
            with self.conn_mgr.get_connection() as conn:
                cursor = conn.cursor()

                query = "SELECT * FROM messages WHERE session_id = ?"
                params = [session_id]

                if after_timestamp is not None:
                    query += " AND timestamp > ?"
                    params.append(after_timestamp)

                query += " ORDER BY timestamp ASC"

                if limit is not None:
                    query += " LIMIT ?"
                    params.append(limit)

                cursor.execute(query, params)
                rows = cursor.fetchall()

                return [self._row_to_message(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting messages by session: {e}", exc_info=True)
            return []

    async def update_recalled_status(self, message_id: str, is_recalled: bool) -> bool:
        try:
            with self.conn_mgr.transaction() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE messages
                    SET is_recalled = ?
                    WHERE id = ?
                """, (is_recalled, message_id))
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating recalled status: {e}", exc_info=True)
            return False

    async def update_read_status_until(
        self, session_id: str, until_timestamp: float, is_read: bool = True
    ) -> int:
        """
        Mark messages in a session as read/unread up to a timestamp.
        Returns number of affected rows.
        """
        try:
            with self.conn_mgr.transaction() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    UPDATE messages
                    SET is_read = ?
                    WHERE session_id = ?
                      AND timestamp <= ?
                      AND is_recalled = FALSE
                    """,
                    (is_read, session_id, until_timestamp),
                )
                return cursor.rowcount or 0
        except Exception as e:
            logger.error(f"Error updating read status: {e}", exc_info=True)
            return 0

    async def get_last_read_timestamp(self, session_id: str) -> float:
        """Return latest timestamp among read messages in a session."""
        try:
            with self.conn_mgr.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT MAX(timestamp) AS ts
                    FROM messages
                    WHERE session_id = ?
                      AND is_read = TRUE
                      AND is_recalled = FALSE
                    """,
                    (session_id,),
                )
                row = cursor.fetchone()
                return float(row["ts"]) if row and row["ts"] is not None else 0.0
        except Exception as e:
            logger.error(f"Error getting last read timestamp: {e}", exc_info=True)
            return 0.0

    async def delete_by_session(self, session_id: str) -> bool:
        try:
            with self.conn_mgr.transaction() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
                return True
        except Exception as e:
            logger.error(f"Error deleting messages by session: {e}", exc_info=True)
            return False

    async def delete_by_type(self, session_id: str, message_type: str) -> bool:
        try:
            with self.conn_mgr.transaction() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM messages
                    WHERE session_id = ? AND type = ?
                """, (session_id, message_type))
                return True
        except Exception as e:
            logger.error(f"Error deleting messages by type: {e}", exc_info=True)
            return False

    def _row_to_message(self, row) -> Message:
        metadata = json.loads(row['metadata']) if row['metadata'] else {}
        return Message(
            id=row['id'],
            session_id=row['session_id'],
            sender_id=row['sender_id'],
            type=MessageType(row['type']),
            content=row['content'],
            metadata=metadata,
            is_recalled=bool(row['is_recalled']),
            is_read=bool(row['is_read']),
            timestamp=row['timestamp']
        )
