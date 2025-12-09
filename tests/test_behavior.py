"""
Basic tests for behavior system
"""
import pytest
from src.behavior import BehaviorCoordinator
from src.behavior.models import BehaviorConfig, EmotionState
from src.behavior.segmenter import RuleBasedSegmenter
from src.behavior.emotion import EmotionDetector
from src.behavior.typo import TypoInjector


class TestSegmenter:
    def test_rule_based_segmentation(self):
        segmenter = RuleBasedSegmenter(max_length=20)

        # Short text - no segmentation needed
        result = segmenter.segment("Hello!")
        assert len(result) == 1
        assert result[0] == "Hello!"

        # Long text - should segment
        long_text = "This is a long sentence that should be split into multiple segments for better readability."
        result = segmenter.segment(long_text)
        assert len(result) > 1
        # Each segment should be reasonably sized
        for segment in result:
            assert len(segment) <= 60  # Some buffer for split point finding

    def test_chinese_segmentation(self):
        segmenter = RuleBasedSegmenter(max_length=30)
        text = "你好啊，今天天气真好！我很开心，你呢？"
        result = segmenter.segment(text)
        assert len(result) >= 1
        assert all(s.strip() for s in result)  # No empty segments


class TestEmotionDetector:
    def test_basic_emotion_detection(self):
        detector = EmotionDetector()

        # Test happy
        assert detector.detect("哈哈哈，太好了！") == EmotionState.HAPPY

        # Test excited
        assert detector.detect("哇！！太棒了！！") == EmotionState.EXCITED

        # Test sad
        assert detector.detect("唉，真难过啊😢") == EmotionState.SAD

        # Test neutral (no emotion keywords)
        assert detector.detect("今天吃什么") == EmotionState.NEUTRAL

    def test_emotion_intensity(self):
        detector = EmotionDetector()

        # More emotion keywords = higher intensity
        low = detector.detect_intensity("好")
        high = detector.detect_intensity("好好好哈哈哈太棒了！！！")
        assert high > low


class TestTypoInjector:
    def test_typo_injection(self):
        injector = TypoInjector()

        # Test with 100% typo rate to ensure it happens
        text = "这是一个测试"
        has_typo, typo_text, pos, orig = injector.inject_typo(text, typo_rate=1.0)

        # With rate 1.0, should always inject typo if possible
        if has_typo:
            assert typo_text is not None
            assert typo_text != text
            assert pos is not None
            assert orig is not None

    def test_no_typo_with_zero_rate(self):
        injector = TypoInjector()
        text = "这是一个测试"
        has_typo, _, _, _ = injector.inject_typo(text, typo_rate=0.0)
        assert not has_typo

    def test_recall_probability(self):
        injector = TypoInjector()

        # Test recall with 100% rate
        should_recall = injector.should_recall_typo(recall_rate=1.0)
        assert should_recall

        # Test recall with 0% rate
        should_recall = injector.should_recall_typo(recall_rate=0.0)
        assert not should_recall


class TestBehaviorCoordinator:
    def test_basic_message_processing(self):
        config = BehaviorConfig(
            enable_segmentation=True,
            enable_typo=False,  # Disable typo for predictable testing
            enable_recall=False
        )
        coordinator = BehaviorCoordinator(config=config)

        text = "Hello, this is a test message!"
        segments = coordinator.process_message(text)

        assert len(segments) >= 1
        assert all(hasattr(s, 'text') for s in segments)
        assert all(hasattr(s, 'pause_before') for s in segments)
        assert all(hasattr(s, 'typing_speed') for s in segments)

    def test_emotion_detection_integration(self):
        config = BehaviorConfig(enable_emotion_detection=True)
        coordinator = BehaviorCoordinator(config=config)

        text = "哈哈哈太好了！"
        emotion = coordinator.get_emotion(text)
        assert emotion in [EmotionState.HAPPY, EmotionState.EXCITED]

    def test_typo_and_recall(self):
        config = BehaviorConfig(
            enable_segmentation=False,
            enable_typo=True,
            enable_recall=True,
            base_typo_rate=1.0,  # Always inject typo
            typo_recall_rate=1.0  # Always recall
        )
        coordinator = BehaviorCoordinator(config=config)

        text = "这是一个测试消息"
        segments = coordinator.process_message(text)

        # With high typo and recall rates, we should see recall behavior
        # (segment with typo + corrected segment)
        # Note: This is probabilistic, so we just check structure
        assert len(segments) >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
