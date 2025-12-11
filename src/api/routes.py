import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from src.infrastructure.database.connection import DatabaseConnection
from src.services.character.character_service import CharacterService
from src.services.config.config_service import ConfigService
from src.services.messaging.message_service import MessageService
from src.infrastructure.database.repositories import (
    MessageRepository,
    CharacterRepository,
    SessionRepository,
    ConfigRepository,
)
from src.core.config import database_config
from src.core.models.constants import DEFAULT_USER_ID

logger = logging.getLogger(__name__)

router = APIRouter()

# Service instances
db_connection: Optional[DatabaseConnection] = None
character_service: Optional[CharacterService] = None
config_service: Optional[ConfigService] = None
message_service: Optional[MessageService] = None
session_repo: Optional[SessionRepository] = None


async def initialize_services():
    global db_connection, character_service, config_service, message_service, session_repo

    if db_connection is None:
        db_connection = DatabaseConnection(database_config.path)

        # Create repositories
        message_repo = MessageRepository(db_connection)
        character_repo = CharacterRepository(db_connection)
        session_repo = SessionRepository(db_connection)
        config_repo = ConfigRepository(db_connection)

        # Create services
        message_service = MessageService(message_repo)
        config_service = ConfigService(config_repo)
        character_service = CharacterService(
            character_repo, session_repo, message_service, config_service
        )

        await character_service.initialize_builtin_characters()
        logger.info("REST API services initialized")


class CharacterCreate(BaseModel):
    name: str
    avatar: str
    persona: str
    behavior_params: Optional[Dict[str, Any]] = None


class CharacterUpdate(BaseModel):
    name: Optional[str] = None
    avatar: Optional[str] = None
    persona: Optional[str] = None
    behavior_params: Optional[Dict[str, Any]] = None


class ConfigUpdate(BaseModel):
    config: Dict[str, str]


@router.get("/characters")
async def get_characters():
    await initialize_services()
    characters = await character_service.get_all_characters()
    return {"characters": [char.model_dump() for char in characters]}


@router.get("/characters/{character_id}")
async def get_character(character_id: str):
    await initialize_services()
    character = await character_service.get_character(character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    return {"character": character.model_dump()}


@router.post("/characters")
async def create_character(data: CharacterCreate):
    await initialize_services()

    character = await character_service.create_character(
        name=data.name,
        avatar=data.avatar,
        persona=data.persona,
        behavior_params=data.behavior_params,
    )

    if not character:
        raise HTTPException(status_code=500, detail="Failed to create character")

    return {"character": character.model_dump()}


@router.put("/characters/{character_id}")
async def update_character(character_id: str, data: CharacterUpdate):
    await initialize_services()

    character = await character_service.get_character(character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    if character.is_builtin:
        raise HTTPException(status_code=403, detail="Cannot modify builtin character")

    if data.name is not None:
        character.name = data.name
    if data.avatar is not None:
        character.avatar = data.avatar
    if data.persona is not None:
        character.persona = data.persona
    if data.behavior_params:
        for key, value in data.behavior_params.items():
            if hasattr(character, key):
                setattr(character, key, value)

    success = await character_service.update_character(character)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update character")

    return {"character": character.model_dump()}


@router.delete("/characters/{character_id}")
async def delete_character(character_id: str):
    await initialize_services()

    success = await character_service.delete_character(character_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete character")

    return {"success": True}


@router.get("/sessions")
async def get_sessions():
    await initialize_services()
    sessions = await session_repo.get_all()
    return {"sessions": [sess.model_dump() for sess in sessions]}


@router.get("/sessions/active")
async def get_active_session():
    await initialize_services()
    session = await session_repo.get_active_session()
    if not session:
        return {"session": None}
    return {"session": session.model_dump()}


@router.post("/sessions/{session_id}/activate")
async def activate_session(session_id: str):
    await initialize_services()

    success = await character_service.switch_active_session(session_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to activate session")

    return {"success": True}


@router.get("/sessions/{session_id}/messages")
async def get_session_messages(session_id: str, after: float = 0):
    """
    Incremental message sync over HTTP.
    Returns all messages with timestamp > after.
    """
    await initialize_services()
    messages = await message_service.get_messages(session_id, after)
    return {
        "messages": [
            {
                "id": msg.id,
                "session_id": msg.session_id,
                "sender_id": msg.sender_id,
                "type": msg.type,
                "content": msg.content,
                "metadata": msg.metadata,
                "is_recalled": msg.is_recalled,
                "is_read": msg.is_read,
                "timestamp": msg.timestamp,
            }
            for msg in messages
        ]
    }


@router.get("/config")
async def get_config():
    await initialize_services()
    config = await config_service.get_all_config()
    return {"config": config}


@router.post("/config")
async def update_config(data: ConfigUpdate):
    await initialize_services()

    success = await config_service.set_config(data.config)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update config")

    return {"success": True}


@router.get("/hash")
async def get_hash():
    await initialize_services()
    hash_value = await config_service.compute_hash()
    return {"hash": hash_value}


@router.get("/avatar")
async def get_user_avatar(user_id: str = DEFAULT_USER_ID):
    await initialize_services()
    avatar = await config_service.get_user_avatar(user_id)
    return {"avatar": avatar}


@router.post("/avatar")
async def upload_user_avatar(avatar_data: str, user_id: str = DEFAULT_USER_ID):
    await initialize_services()

    success = await config_service.set_user_avatar(avatar_data, user_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to upload avatar")

    return {"success": True}


@router.delete("/avatar")
async def delete_user_avatar(user_id: str = DEFAULT_USER_ID):
    await initialize_services()

    success = await config_service.delete_user_avatar(user_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete avatar")

    return {"success": True}
