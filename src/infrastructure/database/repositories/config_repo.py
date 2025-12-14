import logging
import hashlib
import json
from typing import List, Optional, Dict
from src.infrastructure.database.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class ConfigRepository(BaseRepository[Dict]):
    async def get_by_id(self, id: str) -> Optional[Dict]:
        return await self.get_config(id)

    async def get_all(self) -> List[Dict]:
        config = await self.get_all_config()
        return [{"key": k, "value": v} for k, v in config.items()]

    async def create(self, entity: Dict) -> bool:
        return await self.set_config(entity.get("key"), entity.get("value"))

    async def update(self, entity: Dict) -> bool:
        return await self.set_config(entity.get("key"), entity.get("value"))

    async def delete(self, id: str) -> bool:
        try:
            with self.conn_mgr.transaction() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM app_config WHERE key = ?", (id,))
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting config: {e}", exc_info=True)
            return False

    async def get_config(self, key: str) -> Optional[str]:
        try:
            with self.conn_mgr.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM app_config WHERE key = ?", (key,))
                row = cursor.fetchone()
                return row['value'] if row else None
        except Exception as e:
            logger.error(f"Error getting config: {e}", exc_info=True)
            return None

    async def get_all_config(self) -> Dict[str, str]:
        try:
            with self.conn_mgr.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT key, value FROM app_config")
                rows = cursor.fetchall()
                return {row['key']: row['value'] for row in rows}
        except Exception as e:
            logger.error(f"Error getting all config: {e}", exc_info=True)
            return {}

    async def set_config(self, key: str, value: str) -> bool:
        try:
            with self.conn_mgr.transaction() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO app_config (key, value, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(key) DO UPDATE SET
                        value = excluded.value,
                        updated_at = CURRENT_TIMESTAMP
                    """,
                    (key, value),
                )
                return True
        except Exception as e:
            logger.error(f"Error setting config: {e}", exc_info=True)
            return False

    async def set_config_batch(self, config: Dict[str, str]) -> bool:
        try:
            with self.conn_mgr.transaction() as conn:
                cursor = conn.cursor()
                for key, value in config.items():
                    cursor.execute(
                        """
                        INSERT INTO app_config (key, value, updated_at)
                        VALUES (?, ?, CURRENT_TIMESTAMP)
                        ON CONFLICT(key) DO UPDATE SET
                            value = excluded.value,
                            updated_at = CURRENT_TIMESTAMP
                        """,
                        (key, value),
                    )
                return True
        except Exception as e:
            logger.error(f"Error setting config batch: {e}", exc_info=True)
            return False

    async def get_user_avatar(self, user_id: str) -> Optional[str]:
        try:
            with self.conn_mgr.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT avatar_data FROM user_settings WHERE user_id = ?", (user_id,))
                row = cursor.fetchone()
                return row['avatar_data'] if row else None
        except Exception as e:
            logger.error(f"Error getting user avatar: {e}", exc_info=True)
            return None

    async def set_user_avatar(self, avatar_data: str, user_id: str) -> bool:
        try:
            with self.conn_mgr.transaction() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO user_settings (user_id, avatar_data, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(user_id) DO UPDATE SET
                        avatar_data = excluded.avatar_data,
                        updated_at = CURRENT_TIMESTAMP
                """, (user_id, avatar_data))
                return True
        except Exception as e:
            logger.error(f"Error setting user avatar: {e}", exc_info=True)
            return False

    async def delete_user_avatar(self, user_id: str) -> bool:
        try:
            with self.conn_mgr.transaction() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE user_settings
                    SET avatar_data = NULL, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                """, (user_id,))
                return True
        except Exception as e:
            logger.error(f"Error deleting user avatar: {e}", exc_info=True)
            return False

    async def compute_hash(self, table: str) -> str:
        try:
            with self.conn_mgr.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT * FROM {table} ORDER BY rowid")
                rows = cursor.fetchall()

                content = json.dumps([dict(row) for row in rows], sort_keys=True)
                return hashlib.sha256(content.encode()).hexdigest()
        except Exception as e:
            logger.error(f"Error computing hash for table {table}: {e}", exc_info=True)
            return ""
