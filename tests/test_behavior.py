"""
Basic tests for behavior system
"""
import pytest

from src.behavior import BehaviorCoordinator
from src.behavior.emotion import EmotionDetector
from src.behavior.models import BehaviorConfig, EmotionState
from src.behavior.segmenter import RuleBasedSegmenter
from src.behavior.typo import TypoInjector


class TestSegmenter:
    def test_rule_based_segmentation(self):
        segmenter = RuleBasedSegmenter(max_length=20)

        result = segmenter.segment("Hello!")
        assert len(result) == 1
        assert result[0] == "Hello!"

        long_text = "Part A, part B, part C - and then another clause."
        result = segmenter.segment(long_text)
        assert len(result) >= 2
        for segment in result:
            assert segment.strip()

    def test_chinese_segmentation(self):
        segmenter = RuleBasedSegmenter(max_length=30)
        text = "你好啊，今天天气真好！我很开心，你呢？"
        result = segmenter.segment(text)
        assert len(result) >= 1
        assert all(s.strip() for s in result)


class TestEmotionDetector:
    def test_basic_emotion_detection(self):
        detector = EmotionDetector()
        emotion_map = {
            "happy": "medium",
            "excited": "high",
            "sad": "low",
        }
        assert detector.detect(emotion_map) == EmotionState.EXCITED

    def test_invalid_values_fall_back_to_neutral(self):
        detector = EmotionDetector()
        assert detector.detect({"unknown": "mid"}) == EmotionState.NEUTRAL

    def test_additional_emotions_are_mapped(self):
        detector = EmotionDetector()
        emotion_map = {"surprised": "high"}
        assert detector.detect(emotion_map) == EmotionState.EXCITED


class TestTypoInjector:
    def test_typo_injection(self):
        injector = TypoInjector()
        text = "这是一个测试"
        has_typo, typo_text, pos, orig = injector.inject_typo(text, typo_rate=1.0)

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
        assert injector.should_recall_typo(recall_rate=1.0)
        assert not injector.should_recall_typo(recall_rate=0.0)


class TestBehaviorCoordinator:
    def test_basic_message_processing(self):
        config = BehaviorConfig(
            enable_segmentation=True,
            enable_typo=False,
            enable_recall=False,
        )
        coordinator = BehaviorCoordinator(config=config)

        text = "Hello, this is a test message!"
        actions = coordinator.process_message(text)

        assert len(actions) >= 1
        send_actions = [a for a in actions if a.type == "send"]
        assert send_actions

    def test_emotion_detection_integration(self):
        config = BehaviorConfig(enable_emotion_detection=True)
        coordinator = BehaviorCoordinator(config=config)

        text = "哈哈哈太好了！"
        emotion = coordinator.get_emotion(text, emotion_map={"happy": "medium"})
        assert emotion in [EmotionState.HAPPY, EmotionState.EXCITED]

    def test_typo_and_recall(self):
        config = BehaviorConfig(
            enable_segmentation=False,
            enable_typo=True,
            enable_recall=True,
            base_typo_rate=1.0,
            typo_recall_rate=1.0,
        )
        coordinator = BehaviorCoordinator(config=config)

        text = "这是一个测试消息"
        actions = coordinator.process_message(text)

        recall_actions = [a for a in actions if a.type == "recall"]
        assert recall_actions, "Recall action should be present when typo+recall always true"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
