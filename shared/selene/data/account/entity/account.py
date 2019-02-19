from datetime import date
from dataclasses import dataclass
from typing import List


@dataclass
class AccountAgreement(object):
    """Representation of a 'signed' agreement"""
    type: str
    accept_date: date
    id: str = None


@dataclass
class AccountSubscription(object):
    """Represents the subscription plan chosen by the user"""
    type: str
    start_date: date
    stripe_customer_id: str
    id: str = None


@dataclass
class Account(object):
    """Representation of a Mycroft user account."""
    email_address: str
    username: str
    agreements: List[AccountAgreement]
    subscription: AccountSubscription
    id: str = None
    refresh_tokens: List[str] = None
