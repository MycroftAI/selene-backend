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
from dataclasses import asdict
from datetime import datetime

from hamcrest import assert_that, equal_to, greater_than

from selene.data.metric import AccountActivityRepository


def get_account_activity(db):
    acct_activity_repository = AccountActivityRepository(db)
    return acct_activity_repository.get_activity_by_date(datetime.utcnow().date())


def remove_account_activity(db):
    acct_activity_repository = AccountActivityRepository(db)
    acct_activity_repository.delete_activity_by_date(datetime.utcnow().date())


def check_account_metrics(context, total, changed):
    """Abstract function for checking that account activity metrics were updated."""
    acct_activity_repository = AccountActivityRepository(context.db)
    account_activity = acct_activity_repository.get_activity_by_date(
        datetime.utcnow().date()
    )
    before = asdict(context.account_activity)
    after = asdict(account_activity)
    if context.account_activity is None:
        assert_that(after[total], greater_than(0))
        assert_that(after[changed], equal_to(1))
    else:
        if "added" in changed:
            assert_that(after[total], equal_to(before[total] + 1))
        else:
            assert_that(after[total], equal_to(before[total] - 1))
        assert_that(after[changed], equal_to(before[changed] + 1))
