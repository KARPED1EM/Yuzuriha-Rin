"""
Emotion interpretation module.

Emotion data now comes from the LLM as a map of emotion -> intensity.
We convert that structure into a primary EmotionState for downstream logic.
"""

from typing import Dict

from src.behavior.models import EmotionState


class EmotionFetcher:
    """Interpret LLM-supplied emotion maps."""

    INTENSITY_ORDER = ["low", "medium", "high", "extreme"]
    NAME_TO_STATE = {
        "neutral": EmotionState.NEUTRAL,
        "happy": EmotionState.HAPPY,
        "excited": EmotionState.EXCITED,
        "sad": EmotionState.SAD,
        "angry": EmotionState.ANGRY,
        "mad": EmotionState.ANGRY,
        "anxious": EmotionState.ANXIOUS,
        "nervous": EmotionState.ANXIOUS,
        "confused": EmotionState.CONFUSED,
        "shy": EmotionState.CONFUSED,
        "embarrassed": EmotionState.ANXIOUS,
        "surprised": EmotionState.EXCITED,
        "playful": EmotionState.HAPPY,
        "affectionate": EmotionState.HAPPY,
        "tired": EmotionState.SAD,
        "bored": EmotionState.SAD,
        "serious": EmotionState.NEUTRAL,
        "caring": EmotionState.HAPPY,
    }

    def fetch(
        self,
        emotion_map: Dict[str, str] | None = None,
        fallback_text: str | None = None,
    ) -> EmotionState:
        """
        Convert an emotion map into a primary EmotionState.

        Args:
            emotion_map: Dict of {emotion: intensity}, intensity in {low, medium, high, extreme}
            fallback_text: Unused placeholder for compatibility (kept for future heuristics)
        """
        if not emotion_map:
            return EmotionState.NEUTRAL

        normalized = self._normalize_map(emotion_map)
        if not normalized:
            return EmotionState.NEUTRAL

        top_emotion, _ = max(
            normalized.items(),
            key=lambda item: self._intensity_rank(item[1]),
        )
        return self.NAME_TO_STATE.get(top_emotion, EmotionState.NEUTRAL)

    def normalize_map(self, emotion_map: Dict[str, str] | None) -> Dict[str, str]:
        """Public helper to normalize raw emotion maps into lowercase keys/values."""
        if not emotion_map:
            return {}
        return self._normalize_map(emotion_map)

    def _normalize_map(self, emotion_map: Dict[str, str]) -> Dict[str, str]:
        cleaned: Dict[str, str] = {}
        for raw_key, raw_value in emotion_map.items():
            key = str(raw_key).strip().lower()
            value = str(raw_value).strip().lower()
            if not key:
                continue
            if value not in self.INTENSITY_ORDER:
                continue
            cleaned[key] = value
        return cleaned

    def _intensity_rank(self, intensity: str) -> int:
        try:
            return self.INTENSITY_ORDER.index(intensity)
        except ValueError:
            return 0
