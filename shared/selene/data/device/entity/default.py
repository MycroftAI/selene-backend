from dataclasses import dataclass

from selene.data.geography import City, Country, Region, Timezone
from .text_to_speech import TextToSpeech
from .wake_word import WakeWord


@dataclass
class AccountDefaults(object):
    city: City = None
    country: Country = None
    region: Region = None
    timezone: Timezone = None
    voice: TextToSpeech = None
    wake_word: WakeWord = None
    id: str = None
