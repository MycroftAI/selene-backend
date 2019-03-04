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
