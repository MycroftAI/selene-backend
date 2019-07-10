from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class CoreMetric(object):
    device_id: str
    metric_type: str
    metric_value: dict
    id: str = None


@dataclass
class CoreInteraction(object):
    core_id: str
    device_id: str
    start_ts: datetime
    stt_engine: str = None
    stt_transcription: str = None
    stt_duration: Decimal = None
    intent_type: str = None
    intent_duration: Decimal = None
    fallback_handler_duration: Decimal = None
    skill_handler: str = None
    skill_duration: Decimal = None
    tts_engine: str = None
    tts_utterance: str = None
    tts_duration: str = None
    speech_playback_duration: Decimal = None
    user_latency: Decimal = None
    id: str = None
