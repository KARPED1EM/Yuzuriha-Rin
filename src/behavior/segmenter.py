"""
Message Segmentation Module

Provides interface for message segmentation with both rule-based and ML-based implementations.
The ML implementation can be easily swapped in when the BiLSTM-CRF model is ready.
"""
import re
from abc import ABC, abstractmethod
from typing import List
import random


class BaseSegmenter(ABC):
    """Abstract base class for message segmentation"""

    @abstractmethod
    def segment(self, text: str) -> List[str]:
        """
        Segment a message into natural chunks

        Args:
            text: Input message text

        Returns:
            List of text segments
        """
        pass


class RuleBasedSegmenter(BaseSegmenter):
    """
    Rule-based segmenter using punctuation and length heuristics.
    This serves as a fallback and baseline until the ML model is trained.
    """

    def __init__(self, max_length: int = 50):
        self.max_length = max_length
        # Common split points in Chinese/English
        self.split_patterns = [
            r'[。！？\.\!\?]+',  # Sentence endings
            r'[,，、]',  # Commas
            r'[;；]',  # Semicolons
            r'[\s]+',  # Whitespace
        ]

    def segment(self, text: str) -> List[str]:
        """Segment text using rules"""
        if not text or len(text) <= self.max_length:
            return [text] if text else []

        segments = []
        current_pos = 0

        while current_pos < len(text):
            # Try to find a good split point within max_length
            end_pos = min(current_pos + self.max_length, len(text))

            if end_pos == len(text):
                # Last segment
                segments.append(text[current_pos:end_pos].strip())
                break

            # Look for natural break points
            segment_text = text[current_pos:end_pos]
            best_split = self._find_best_split(segment_text)

            if best_split > 0:
                segments.append(text[current_pos:current_pos + best_split].strip())
                current_pos += best_split
            else:
                # No good split found, just use max_length
                segments.append(segment_text.strip())
                current_pos = end_pos

        return [s for s in segments if s]  # Filter empty segments

    def _find_best_split(self, text: str) -> int:
        """Find the best position to split the text"""
        # Try each pattern in order of priority
        for pattern in self.split_patterns:
            matches = list(re.finditer(pattern, text))
            if matches:
                # Use the last match (rightmost split point)
                last_match = matches[-1]
                return last_match.end()

        return 0  # No split point found


class MLSegmenter(BaseSegmenter):
    """
    ML-based segmenter using BiLSTM-CRF model (to be implemented).
    This class provides the interface for future ML integration.
    """

    def __init__(self, model_path: str = None):
        self.model_path = model_path
        self.model = None
        self._load_model()

    def _load_model(self):
        """Load the trained BiLSTM-CRF model"""
        if self.model_path:
            # TODO: Implement model loading when training is complete
            # Example:
            # import torch
            # self.model = torch.load(self.model_path)
            # self.model.eval()
            pass

    def segment(self, text: str) -> List[str]:
        """
        Segment text using ML model.
        Falls back to rule-based if model not available.
        """
        if self.model is None:
            # Fallback to rule-based
            fallback = RuleBasedSegmenter()
            return fallback.segment(text)

        # TODO: Implement ML-based segmentation
        # Example workflow:
        # 1. Tokenize text
        # 2. Convert to model input format
        # 3. Run inference
        # 4. Extract segment boundaries from predictions
        # 5. Split text accordingly

        raise NotImplementedError("ML segmentation will be implemented after model training")


class SmartSegmenter(BaseSegmenter):
    """
    Smart segmenter that automatically chooses between rule-based and ML-based
    segmentation based on model availability.
    """

    def __init__(self, model_path: str = None, max_length: int = 50):
        self.max_length = max_length
        self.ml_segmenter = None
        self.rule_segmenter = RuleBasedSegmenter(max_length)

        # Try to initialize ML segmenter if model path provided
        if model_path:
            try:
                self.ml_segmenter = MLSegmenter(model_path)
                if self.ml_segmenter.model is not None:
                    print(f"✓ ML segmenter loaded from {model_path}")
            except Exception as e:
                print(f"⚠ ML segmenter unavailable, using rule-based: {e}")

    def segment(self, text: str) -> List[str]:
        """Use ML segmenter if available, otherwise fall back to rules"""
        if self.ml_segmenter and self.ml_segmenter.model:
            try:
                return self.ml_segmenter.segment(text)
            except Exception as e:
                print(f"⚠ ML segmentation failed, falling back to rules: {e}")

        return self.rule_segmenter.segment(text)
