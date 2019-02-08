from datetime import date
from dataclasses import dataclass
from typing import List


@dataclass
class AccountAgreement(object):
    """Representation of a 'signed' agreement"""
    agreement: str
    signature_date: date


@dataclass
class AccountSubscription(object):
    """Represents the subscription plan chosen by the user"""
    subscription_type: str
    start_date: date


@dataclass
class Account(object):
    """Representation of a Mycroft user account."""
    id: str
    email_address: str
    refresh_tokens: List[str]
    agreements: List[AccountAgreement]
    subscription: AccountSubscription
