"""
Behavior Coordinator

Orchestrates all behavior components to create natural message patterns.
This is the main entry point for the behavior system.
"""
from typing import List
import random

from .models import MessageSegment, BehaviorConfig, EmotionState
from .segmenter import SmartSegmenter
from .emotion import EmotionDetector
from .typo import TypoInjector
from .pause import PausePredictor


class BehaviorCoordinator:
    """
    Coordinates message segmentation, typo injection, and recall behaviors
    to create natural human-like message patterns.
    """

    def __init__(self, config: BehaviorConfig = None, model_path: str = None):
        """
        Initialize the behavior coordinator

        Args:
            config: Behavior configuration
            model_path: Optional path to trained segmentation model
        """
        self.config = config or BehaviorConfig()

        # Initialize components
        self.segmenter = SmartSegmenter(
            model_path=model_path,
            max_length=self.config.max_segment_length
        )
        self.emotion_detector = EmotionDetector()
        self.typo_injector = TypoInjector()
        self.pause_predictor = PausePredictor()

    def process_message(self, text: str) -> List[MessageSegment]:
        """
        Process a message and generate segments with natural behaviors

        Args:
            text: Input message text

        Returns:
            List of MessageSegment objects with behaviors applied
        """
        # Step 1: Detect emotion
        emotion = EmotionState.NEUTRAL
        if self.config.enable_emotion_detection:
            emotion = self.emotion_detector.detect(text)

        # Step 2: Segment the message
        segments_text = [text]  # Default: no segmentation
        if self.config.enable_segmentation:
            segments_text = self.segmenter.segment(text)

        # Step 3: Process each segment
        segments = []
        for i, segment_text in enumerate(segments_text):
            is_first = (i == 0)
            is_last = (i == len(segments_text) - 1)

            # Predict pause duration
            pause = self.pause_predictor.predict(
                segment_text,
                emotion=emotion,
                is_first=is_first,
                is_last=is_last
            )

            # Predict typing speed
            typing_speed = self.pause_predictor.predict_typing_speed(emotion)

            # Try to inject typo
            has_typo = False
            typo_text = None
            typo_pos = None
            original_char = None

            if self.config.enable_typo:
                # Calculate typo rate based on emotion
                emotion_multiplier = self.config.emotion_typo_multiplier.get(
                    emotion, 1.0
                )
                typo_rate = self.config.base_typo_rate * emotion_multiplier

                has_typo, typo_text, typo_pos, original_char = self.typo_injector.inject_typo(
                    segment_text,
                    typo_rate=typo_rate
                )

            # Create segment
            segment = MessageSegment(
                text=segment_text,
                pause_before=pause,
                typing_speed=typing_speed,
                has_typo=has_typo,
                typo_position=typo_pos,
                typo_char=typo_text[typo_pos] if (has_typo and typo_text and typo_pos is not None) else None
            )

            segments.append(segment)

            # If typo was injected, decide whether to recall
            if has_typo and self.config.enable_recall:
                should_recall = self.typo_injector.should_recall_typo(
                    self.config.typo_recall_rate
                )

                if should_recall and typo_text:
                    # Add typo segment
                    typo_segment = MessageSegment(
                        text=typo_text,
                        pause_before=pause,
                        typing_speed=typing_speed,
                        has_typo=True,
                        typo_position=typo_pos,
                        typo_char=segment.typo_char
                    )
                    segments[-1] = typo_segment  # Replace with typo version

                    # Add corrected segment after recall delay
                    corrected_segment = MessageSegment(
                        text=segment_text,  # Original correct text
                        pause_before=self.config.retype_delay,
                        typing_speed=typing_speed,
                        has_typo=False
                    )
                    segments.append(corrected_segment)

        return segments

    def update_config(self, config: BehaviorConfig):
        """Update behavior configuration"""
        self.config = config

    def get_emotion(self, text: str) -> EmotionState:
        """Get detected emotion for text"""
        return self.emotion_detector.detect(text)
