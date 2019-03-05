from dataclasses import dataclass

from .geography import Geography
from .text_to_speech import TextToSpeech
from .wake_word import WakeWord


@dataclass
class AccountPreferences(object):
    id: str
    date_format: str
    time_format: str
    measurement_system: str
    geography: Geography = None
    voice: TextToSpeech = None
    wake_word: WakeWord = None
