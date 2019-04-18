from dataclasses import dataclass
from datetime import datetime

from selene.data.geography import City, Country, Region, Timezone
from .text_to_speech import TextToSpeech
from .wake_word import WakeWord


@dataclass
class Device(object):
    """Representation of a Device"""
    account_id: str
    city: City
    country: Country
    core_version: str
    enclosure_version: str
    id: str
    name: str
    platform: str
    region: Region
    text_to_speech: TextToSpeech
    timezone: Timezone
    wake_word: WakeWord
    last_contact_ts: datetime = None
    placement: str = None
