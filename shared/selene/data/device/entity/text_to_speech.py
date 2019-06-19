from dataclasses import dataclass


@dataclass
class TextToSpeech(object):
    setting_name: str
    display_name: str
    engine: str
    id: str = None
