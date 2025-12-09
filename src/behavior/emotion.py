"""
Emotion Detection Module

Simple keyword-based emotion detection. Can be replaced with more
sophisticated NLP models in the future.
"""
import re
from typing import Dict, List
from .models import EmotionState


class EmotionDetector:
    """Detect emotion from text using keyword matching"""

    def __init__(self):
        # Emotion keywords (can be extended or loaded from file)
        self.emotion_keywords: Dict[EmotionState, List[str]] = {
            EmotionState.HAPPY: [
                "哈哈", "嘿嘿", "开心", "高兴", "快乐", "好啊", "太好了", "棒",
                "haha", "hehe", "happy", "glad", "great", "awesome", "nice",
                "😊", "😄", "😁", "🎉", "❤️"
            ],
            EmotionState.EXCITED: [
                "！！", "!!", "哇", "天啊", "真的吗", "太棒了", "超级", "非常",
                "wow", "omg", "amazing", "incredible", "super", "really",
                "🤩", "😍", "🔥", "✨"
            ],
            EmotionState.SAD: [
                "难过", "伤心", "哭", "呜呜", "唉", "可惜", "遗憾", "失望",
                "sad", "cry", "unfortunately", "sorry", "disappointed",
                "😢", "😭", "😔", "💔"
            ],
            EmotionState.ANGRY: [
                "生气", "愤怒", "可恶", "讨厌", "烦", "气死", "混蛋",
                "angry", "mad", "annoyed", "hate", "damn",
                "😠", "😡", "💢"
            ],
            EmotionState.ANXIOUS: [
                "紧张", "担心", "害怕", "焦虑", "不安", "怎么办", "完了",
                "nervous", "worried", "scared", "anxious", "stressed",
                "😰", "😨", "😟"
            ],
            EmotionState.CONFUSED: [
                "？？", "??", "什么", "啊", "哈", "诶", "嗯", "confused", "huh", "what",
                "😕", "🤔", "😵"
            ],
        }

        # Compile patterns for efficiency
        self.emotion_patterns = {
            emotion: re.compile('|'.join(re.escape(kw) for kw in keywords), re.IGNORECASE)
            for emotion, keywords in self.emotion_keywords.items()
        }

    def detect(self, text: str) -> EmotionState:
        """
        Detect the primary emotion in text

        Args:
            text: Input text

        Returns:
            Detected emotion state
        """
        emotion_scores = {}

        for emotion, pattern in self.emotion_patterns.items():
            matches = pattern.findall(text)
            emotion_scores[emotion] = len(matches)

        # Find emotion with highest score
        if emotion_scores:
            max_emotion = max(emotion_scores.items(), key=lambda x: x[1])
            if max_emotion[1] > 0:
                return max_emotion[0]

        return EmotionState.NEUTRAL

    def detect_intensity(self, text: str) -> float:
        """
        Detect the intensity of emotion (0.0 to 1.0)

        Args:
            text: Input text

        Returns:
            Emotion intensity score
        """
        total_matches = 0
        for pattern in self.emotion_patterns.values():
            total_matches += len(pattern.findall(text))

        # Normalize by text length
        if len(text) > 0:
            # More matches per character = higher intensity
            intensity = min(total_matches / (len(text) / 20), 1.0)
            return intensity

        return 0.0
