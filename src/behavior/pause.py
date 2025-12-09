"""
Pause Duration Prediction Module

Predicts natural pause durations between message segments.
Currently uses heuristics, can be replaced with ML model.
"""
import random
from .models import EmotionState


class PausePredictor:
    """Predict pause durations between message segments"""

    def __init__(self):
        # Base pause ranges by emotion (in seconds)
        self.emotion_pause_ranges = {
            EmotionState.NEUTRAL: (0.5, 1.2),
            EmotionState.HAPPY: (0.3, 0.8),
            EmotionState.EXCITED: (0.2, 0.6),
            EmotionState.SAD: (0.8, 2.0),
            EmotionState.ANGRY: (0.3, 1.0),
            EmotionState.ANXIOUS: (0.4, 1.5),
            EmotionState.CONFUSED: (0.6, 1.5),
        }

    def predict(
        self,
        segment_text: str,
        emotion: EmotionState = EmotionState.NEUTRAL,
        is_first: bool = False,
        is_last: bool = False
    ) -> float:
        """
        Predict pause duration before sending a segment

        Args:
            segment_text: The text segment
            emotion: Current emotion state
            is_first: Whether this is the first segment
            is_last: Whether this is the last segment

        Returns:
            Pause duration in seconds
        """
        # No pause before first segment
        if is_first:
            return 0.0

        # Get base pause range for emotion
        min_pause, max_pause = self.emotion_pause_ranges.get(
            emotion,
            (0.5, 1.2)
        )

        # Add randomness
        base_pause = random.uniform(min_pause, max_pause)

        # Adjust based on segment length (longer text = slightly longer pause)
        length_factor = min(len(segment_text) / 30, 1.5)
        pause = base_pause * length_factor

        # Last segment might have slightly longer pause (user "thinking")
        if is_last:
            pause *= random.uniform(1.0, 1.3)

        # Ensure within reasonable bounds
        return max(0.2, min(pause, 3.0))

    def predict_typing_speed(
        self,
        emotion: EmotionState = EmotionState.NEUTRAL
    ) -> float:
        """
        Predict typing speed (seconds per character)

        Args:
            emotion: Current emotion state

        Returns:
            Seconds per character
        """
        # Base typing speeds by emotion
        emotion_speeds = {
            EmotionState.NEUTRAL: 0.05,
            EmotionState.HAPPY: 0.04,
            EmotionState.EXCITED: 0.03,
            EmotionState.SAD: 0.07,
            EmotionState.ANGRY: 0.04,
            EmotionState.ANXIOUS: 0.06,
            EmotionState.CONFUSED: 0.06,
        }

        base_speed = emotion_speeds.get(emotion, 0.05)

        # Add slight randomness
        return base_speed * random.uniform(0.9, 1.1)
