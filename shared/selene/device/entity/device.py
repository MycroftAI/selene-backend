from datetime import datetime
from dataclasses import dataclass


@dataclass
class WakeWord(object):
    id: str
    wake_word: str
    engine: str


@dataclass
class WakeWordSettings(object):
    id: str
    sample_rate: int
    channels: int
    pronunciation: str
    threshold: str
    threshold_multiplier: float
    dynamic_energy_ratio: float


@dataclass
class TextToSpeech(object):
    id: str
    setting_name: str
    display_name: str
    engine: str


@dataclass
class Device(object):
    """Representation of a Device"""
    id: str
    name: str
    platform: str
    enclosure_version: str
    core_version: str
    wake_word: WakeWord
    text_to_speech: TextToSpeech
    placement: str = None
    last_contact_ts: datetime = None
