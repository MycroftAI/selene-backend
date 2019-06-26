from dataclasses import dataclass
from datetime import date

TERMS_OF_USE = 'Terms of Use'
PRIVACY_POLICY = 'Privacy Policy'
OPEN_DATASET = 'Open Dataset'


@dataclass
class Agreement(object):
    type: str
    version: str
    effective_date: date
    id: str = None
    content: str = None
