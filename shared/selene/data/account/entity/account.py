# Mycroft Server - Backend
# Copyright (C) 2019 Mycroft AI Inc
# SPDX-License-Identifier: 	AGPL-3.0-or-later
#
# This file is part of the Mycroft Server.
#
# The Mycroft Server is free software: you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

from dataclasses import dataclass
from datetime import date, datetime
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
    payment_id: str
    id: str = None
    end_date: date = None


@dataclass
class Account(object):
    """Representation of a Mycroft user account."""

    email_address: str
    agreements: List[AccountAgreement]
    last_activity: datetime = None
    membership: AccountMembership = None
    username: str = None
    id: str = None
