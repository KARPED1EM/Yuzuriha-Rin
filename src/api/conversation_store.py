"""
Lightweight in-memory conversation store used to keep chat history on the
server side. This ensures the LLM always receives the full dialogue context
even if the frontend only sends the latest turn.
"""
from typing import Dict, List

from .schemas import ChatMessage


class ConversationStore:
    def __init__(self):
        self._store: Dict[str, List[dict]] = {}

    def merge_history(self, conversation_id: str, incoming: List[ChatMessage]) -> List[ChatMessage]:
        """
        Merge incoming messages into stored history.
        - Stored history is authoritative for assistant outputs (contains typos/recalls).
        - We still accept new user messages from the client payload.
        """
        normalized = [m.dict() for m in incoming]
        existing = self._store.get(conversation_id, [])

        prefix_len = 0
        while (
            prefix_len < len(existing)
            and prefix_len < len(normalized)
            and existing[prefix_len] == normalized[prefix_len]
        ):
            prefix_len += 1

        merged = list(existing)
        if len(existing) > prefix_len:
            # We already have extra assistant/system notes; append only new user turns
            for msg in normalized[prefix_len:]:
                if msg.get("role") == "user":
                    merged.append(msg)
        else:
            merged.extend(normalized[prefix_len:])

        self._store[conversation_id] = merged
        return [ChatMessage(**m) for m in merged]

    def append_assistant_reply(self, conversation_id: str, reply_text: str) -> List[ChatMessage]:
        payload = ChatMessage(role="assistant", content=reply_text)
        self._store.setdefault(conversation_id, []).append(payload.dict())
        return [ChatMessage(**m) for m in self._store[conversation_id]]

    def append_playback_actions(self, conversation_id: str, actions: list) -> List[ChatMessage]:
        """
        Persist assistant playback (including typos/recalls) so the LLM can
        observe prior mistakes/corrections in future turns.
        """
        history = self._store.setdefault(conversation_id, [])
        send_index: Dict[str, str] = {}

        for action in actions:
            if action.type == "send":
                tags = []
                if action.metadata.get("has_typo"):
                    tags.append("[typo]")
                if action.metadata.get("is_correction"):
                    tags.append("[correction]")

                prefix = " ".join(tags).strip()
                content = f"{prefix} {action.text}".strip() if prefix else action.text
                history.append(ChatMessage(role="assistant", content=content).dict())
                if action.message_id:
                    send_index[action.message_id] = content

            elif action.type == "recall":
                recalled = send_index.get(action.target_id, "")
                note = "(assistant recalled a previous message"
                if recalled:
                    note += f": {recalled[:40]}"
                note += ")"
                history.append(ChatMessage(role="system", content=note).dict())

        return [ChatMessage(**m) for m in history]

    def get_history(self, conversation_id: str) -> List[ChatMessage]:
        return [ChatMessage(**m) for m in self._store.get(conversation_id, [])]


conversation_store = ConversationStore()
