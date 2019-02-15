from dataclasses import dataclass
from datetime import date

TERMS_OF_USE = 'Terms of Use'
PRIVACY_POLICY = 'Privacy Policy'


@dataclass
class Agreement(object):
    type: str
    version: str
    content: str
    effective_date: date
    id: str = None
