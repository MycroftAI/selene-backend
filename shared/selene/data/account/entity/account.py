from dataclasses import dataclass
from datetime import date
from typing import List


@dataclass
class AccountAgreement(object):
    """Representation of a 'signed' agreement"""
    type: str
    accept_date: date
    id: str = None


@dataclass
class AccountMembership(object):
    """Represents the subscription plan chosen by the user"""
    type: str
    start_date: date
    payment_method: str
    payment_account_id: str
    id: str = None
    account_id: str = None
    end_date: date = None


@dataclass
class Account(object):
    """Representation of a Mycroft user account."""
    email_address: str
    username: str
    agreements: List[AccountAgreement]
    membership: AccountMembership = None
    id: str = None
    refresh_tokens: List[str] = None
