from functools import lru_cache
from src.infrastructure.database.connection import DatabaseConnection
from src.infrastructure.database.repositories import (
    MessageRepository,
    CharacterRepository,
    SessionRepository,
    ConfigRepository
)
from src.services.messaging.message_service import MessageService
from src.services.character.character_service import CharacterService
from src.services.config.config_service import ConfigService
from src.core.config import database_config


# Database connection singleton
@lru_cache()
def get_db_connection() -> DatabaseConnection:
    return DatabaseConnection(database_config.path)


# Repository dependencies
def get_message_repository() -> MessageRepository:
    conn = get_db_connection()
    return MessageRepository(conn)


def get_character_repository() -> CharacterRepository:
    conn = get_db_connection()
    return CharacterRepository(conn)


def get_session_repository() -> SessionRepository:
    conn = get_db_connection()
    return SessionRepository(conn)


def get_config_repository() -> ConfigRepository:
    conn = get_db_connection()
    return ConfigRepository(conn)


# Service dependencies
@lru_cache()
def get_message_service() -> MessageService:
    message_repo = get_message_repository()
    return MessageService(message_repo)


@lru_cache()
def get_character_service() -> CharacterService:
    character_repo = get_character_repository()
    session_repo = get_session_repository()
    message_service = get_message_service()
    return CharacterService(character_repo, session_repo, message_service)


@lru_cache()
def get_config_service() -> ConfigService:
    config_repo = get_config_repository()
    return ConfigService(config_repo)
