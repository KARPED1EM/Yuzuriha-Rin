"""Behavior configuration models - separated from Character for SRP compliance"""
from pydantic import BaseModel
from src.core.config.defaults import BehaviorDefaults


class TimelineConfig(BaseModel):
    """Timeline behavior configuration"""
    # Hesitation behavior
    hesitation_probability: float = BehaviorDefaults.TIMELINE_HESITATION_PROBABILITY
    hesitation_cycles_min: int = BehaviorDefaults.TIMELINE_HESITATION_CYCLES_MIN
    hesitation_cycles_max: int = BehaviorDefaults.TIMELINE_HESITATION_CYCLES_MAX
    hesitation_duration_min: int = 1500
    hesitation_duration_max: int = 5000
    hesitation_gap_min: int = 500
    hesitation_gap_max: int = 2000
    
    # Typing lead time
    typing_lead_time_threshold_1: int = 6
    typing_lead_time_1: int = 1200
    typing_lead_time_threshold_2: int = 15
    typing_lead_time_2: int = 2000
    typing_lead_time_threshold_3: int = 28
    typing_lead_time_3: int = 3800
    typing_lead_time_threshold_4: int = 34
    typing_lead_time_4: int = 6000
    typing_lead_time_threshold_5: int = 50
    typing_lead_time_5: int = 8800
    typing_lead_time_default: int = 2500
    
    # Entry delay
    entry_delay_min: int = 200
    entry_delay_max: int = 2000
    
    # Initial delay
    initial_delay_weight_1: float = 0.45
    initial_delay_range_1_min: int = 3
    initial_delay_range_1_max: int = 4
    initial_delay_weight_2: float = 0.75
    initial_delay_range_2_min: int = 4
    initial_delay_range_2_max: int = 6
    initial_delay_weight_3: float = 0.93
    initial_delay_range_3_min: int = 6
    initial_delay_range_3_max: int = 7
    initial_delay_range_4_min: int = 8
    initial_delay_range_4_max: int = 9


class SegmenterConfig(BaseModel):
    """Text segmentation configuration"""
    enable: bool = BehaviorDefaults.SEGMENTER_ENABLE
    max_length: int = BehaviorDefaults.SEGMENTER_MAX_LENGTH


class TypoConfig(BaseModel):
    """Typo injection configuration"""
    enable: bool = BehaviorDefaults.TYPO_ENABLE
    base_rate: float = BehaviorDefaults.TYPO_BASE_RATE
    recall_rate: float = BehaviorDefaults.TYPO_RECALL_RATE


class RecallConfig(BaseModel):
    """Message recall configuration"""
    enable: bool = BehaviorDefaults.RECALL_ENABLE
    delay: float = 2.0
    retype_delay: float = 2.5


class PauseConfig(BaseModel):
    """Pause behavior configuration"""
    min_duration: float = 0.8
    max_duration: float = 6.0


class StickerConfig(BaseModel):
    """Sticker sending configuration"""
    send_probability: float = 0.4
    confidence_threshold_positive: float = 0.6
    confidence_threshold_neutral: float = 0.7
    confidence_threshold_negative: float = 0.8


class BehaviorConfig(BaseModel):
    """Complete behavior configuration - aggregates all behavior modules"""
    timeline: TimelineConfig = TimelineConfig()
    segmenter: SegmenterConfig = SegmenterConfig()
    typo: TypoConfig = TypoConfig()
    recall: RecallConfig = RecallConfig()
    pause: PauseConfig = PauseConfig()
    sticker: StickerConfig = StickerConfig()
