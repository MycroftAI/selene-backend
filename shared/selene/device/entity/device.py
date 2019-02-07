from dataclasses import dataclass
from datetime import datetime

from selene.device.entity.text_to_speech import TextToSpeech
from selene.device.entity.wake_word import WakeWord


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
