from dataclasses import dataclass


@dataclass
class WakeWord(object):
    display_name: str
    setting_name: str
    engine: str
    user_defined: bool = False
    id: str = None


@dataclass
class WakeWordSettings(object):
    id: str
    sample_rate: int
    channels: int
    pronunciation: str
    threshold: str
    threshold_multiplier: float
    dynamic_energy_ratio: float
