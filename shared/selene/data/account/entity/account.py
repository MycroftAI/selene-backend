from datetime import date
from dataclasses import dataclass
from typing import List

from validator_collection import validators


@dataclass
class AccountAgreement(object):
    """Representation of a 'signed' agreement"""
    name: str
    signature_date: date


@dataclass
class AccountSubscription(object):
    """Represents the subscription plan chosen by the user"""
    type: str
    start_date: date
    stripe_customer_id: str


@dataclass
class Account(object):
    """Representation of a Mycroft user account."""
    id: str
    email_address: str
    refresh_tokens: List[str]
    agreements: List[AccountAgreement]
    subscription: AccountSubscription

    def __post_init__(self):
        self.email_address = validators.email(self.email_address)
