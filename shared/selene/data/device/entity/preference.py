from dataclasses import dataclass

from .text_to_speech import TextToSpeech
from .wake_word import WakeWord


@dataclass
class AccountPreferences(object):
    id: str
    date_format: str
    time_format: str
    measurement_system: str
    country: str = None
    city: str = None
    region: str = None
    timezone: str = None
    voice: TextToSpeech = None
    wake_word: WakeWord = None
