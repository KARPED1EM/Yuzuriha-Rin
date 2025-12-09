"""
Typo Injection Module

Injects realistic typos based on emotion state and probability.
"""
import random
from typing import Optional, Tuple


class TypoInjector:
    """Inject natural-looking typos into text"""

    def __init__(self):
        # Common typo patterns for Chinese and English
        self.chinese_similar_chars = {
            '的': ['得', '地', '底'],
            '了': ['乐', '啦'],
            '是': ['时', '事'],
            '在': ['再', '载'],
            '吗': ['妈', '马'],
            '呢': ['哪', '内'],
            '我': ['沃', '握'],
            '你': ['您', '尼'],
            '他': ['她', '它'],
            '这': ['着', '遮'],
            '那': ['哪', '纳'],
            '什': ['神', '十'],
            '么': ['嘛', '麽'],
            '会': ['回', '汇'],
            '不': ['步', '布'],
            '要': ['耀', '药'],
            '就': ['旧', '救'],
        }

        self.english_keyboard_neighbors = {
            'q': ['w', 'a'],
            'w': ['q', 'e', 's'],
            'e': ['w', 'r', 'd'],
            'r': ['e', 't', 'f'],
            't': ['r', 'y', 'g'],
            'y': ['t', 'u', 'h'],
            'u': ['y', 'i', 'j'],
            'i': ['u', 'o', 'k'],
            'o': ['i', 'p', 'l'],
            'p': ['o', 'l'],
            'a': ['q', 's', 'z'],
            's': ['a', 'w', 'd', 'x'],
            'd': ['s', 'e', 'f', 'c'],
            'f': ['d', 'r', 'g', 'v'],
            'g': ['f', 't', 'h', 'b'],
            'h': ['g', 'y', 'j', 'n'],
            'j': ['h', 'u', 'k', 'm'],
            'k': ['j', 'i', 'l'],
            'l': ['k', 'o', 'p'],
            'z': ['a', 'x'],
            'x': ['z', 's', 'c'],
            'c': ['x', 'd', 'v'],
            'v': ['c', 'f', 'b'],
            'b': ['v', 'g', 'n'],
            'n': ['b', 'h', 'm'],
            'm': ['n', 'j'],
        }

    def inject_typo(self, text: str, typo_rate: float = 0.08) -> Tuple[bool, Optional[str], Optional[int], Optional[str]]:
        """
        Potentially inject a typo into the text

        Args:
            text: Input text
            typo_rate: Probability of injecting a typo (0.0 to 1.0)

        Returns:
            Tuple of (has_typo, typo_text, typo_position, original_char)
        """
        if not text or random.random() > typo_rate:
            return False, None, None, None

        # Find a suitable position for typo
        # Prefer middle-to-end of text (more realistic)
        min_pos = max(1, len(text) // 3)
        max_pos = len(text)

        # Filter to only positions with replaceable characters
        valid_positions = []
        for i in range(min_pos, max_pos):
            char = text[i]
            if self._can_replace(char):
                valid_positions.append(i)

        if not valid_positions:
            return False, None, None, None

        # Choose random position
        typo_pos = random.choice(valid_positions)
        original_char = text[typo_pos]

        # Generate typo character
        typo_char = self._generate_typo_char(original_char)
        if typo_char is None:
            return False, None, None, None

        # Create typo text
        typo_text = text[:typo_pos] + typo_char + text[typo_pos + 1:]

        return True, typo_text, typo_pos, original_char

    def _can_replace(self, char: str) -> bool:
        """Check if a character can be replaced with a typo"""
        # Chinese characters
        if char in self.chinese_similar_chars:
            return True

        # English letters
        if char.lower() in self.english_keyboard_neighbors:
            return True

        return False

    def _generate_typo_char(self, char: str) -> Optional[str]:
        """Generate a typo replacement for a character"""
        # Chinese typo
        if char in self.chinese_similar_chars:
            return random.choice(self.chinese_similar_chars[char])

        # English typo (keyboard neighbor)
        char_lower = char.lower()
        if char_lower in self.english_keyboard_neighbors:
            neighbor = random.choice(self.english_keyboard_neighbors[char_lower])
            # Preserve case
            if char.isupper():
                return neighbor.upper()
            return neighbor

        return None

    def should_recall_typo(self, recall_rate: float = 0.4) -> bool:
        """
        Decide whether to recall and fix a typo

        Args:
            recall_rate: Probability of recalling (0.0 to 1.0)

        Returns:
            True if should recall
        """
        return random.random() < recall_rate
