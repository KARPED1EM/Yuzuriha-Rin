"""
Message Segmentation Module

Provides interface for message segmentation with rule-based implementations.
"""

from abc import ABC, abstractmethod
from typing import List


class BaseSegmenter(ABC):
    """Abstract base class for message segmentation"""

    @abstractmethod
    def segment(self, text: str) -> List[str]:
        """
        Segment a message into natural chunks.

        Args:
            text: Input message text

        Returns:
            List of text segments
        """
        raise NotImplementedError


class RuleBasedSegmenter(BaseSegmenter):
    """
    Rule-based segmenter using punctuation and dash characters.
    This serves as a fallback and baseline until the mini model is ready.
    """

    def __init__(self, max_length: int):
        self.max_length = max_length
        self.split_tokens = set("。，,！？!?")

    def segment(self, text: str) -> List[str]:
        """Segment text using punctuation boundaries and optional length guard."""
        if not text:
            return []

        segments: List[str] = []
        buffer: List[str] = []

        for char in text:
            buffer.append(char)
            should_split = char in self.split_tokens

            if not should_split and len(buffer) < self.max_length:
                continue

            segment = "".join(buffer).strip()
            if segment:
                segments.append(segment)
            buffer = []

        if buffer:
            remaining = "".join(buffer).strip()
            if remaining:
                segments.append(remaining)

        return segments


class SmartSegmenter(BaseSegmenter):
    """
    Smart segmenter that currently uses rule-based segmentation.
    """

    def __init__(
        self,
        max_length: int,
    ):
        self.rule_segmenter = RuleBasedSegmenter(max_length)

    def segment(self, text: str) -> List[str]:
        """Use rule-based segmentation (LLM-driven structure handled upstream)."""
        return self.rule_segmenter.segment(text)
