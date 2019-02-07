from dataclasses import dataclass


@dataclass
class TextToSpeech(object):
    id: str
    setting_name: str
    display_name: str
    engine: str
