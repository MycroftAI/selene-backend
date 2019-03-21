from dataclasses import dataclass


@dataclass
class Country(object):
    id: str
    iso_code: str
    name: str
