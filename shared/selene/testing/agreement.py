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

import json
from dataclasses import asdict
from datetime import date, timedelta
from typing import Tuple, List

from hamcrest import assert_that, equal_to

from selene.data.account import (
    Agreement,
    AgreementRepository,
    OPEN_DATASET,
    PRIVACY_POLICY,
    TERMS_OF_USE
)


def _build_test_terms_of_use():
    return Agreement(
        type=TERMS_OF_USE,
        version='Holy Grail',
        content='I agree that all the tests I write for this application will '
                'be in the theme of Monty Python and the Holy Grail.  If you '
                'do not agree with these terms, I will be forced to say "Ni!" '
                'until such time as you agree',
        effective_date=date.today() - timedelta(days=1)
)


def _build_test_privacy_policy():
    return Agreement(
        type=PRIVACY_POLICY,
        version='Holy Grail',
        content='First, shalt thou take out the Holy Pin.  Then shalt thou '
                'count to three.  No more.  No less.  Three shalt be the '
                'number thou shalt count and the number of the counting shall '
                'be three.  Four shalt thou not count, nor either count thou '
                'two, excepting that thou then proceed to three.  Five is '
                'right out.  Once the number three, being the third number, '
                'be reached, then lobbest thou Holy Hand Grenade of Antioch '
                'towards thy foe, who, being naughty in My sight, '
                'shall snuff it.',
        effective_date=date.today() - timedelta(days=1)
    )


def _build_open_dataset():
    return Agreement(
        type=OPEN_DATASET,
        version='Holy Grail',
        effective_date=date.today() - timedelta(days=1)
    )


def add_agreements(context):
    """Add agreements to database and set a context variable for each."""
    terms_of_use = _build_test_terms_of_use()
    privacy_policy = _build_test_privacy_policy()
    open_dataset = _build_open_dataset()
    agreement_repository = AgreementRepository(context.db)
    terms_of_use.id = agreement_repository.add(terms_of_use)
    privacy_policy.id = agreement_repository.add(privacy_policy)
    open_dataset.id = agreement_repository.add(open_dataset)
    context.terms_of_use = terms_of_use
    context.privacy_policy = privacy_policy
    context.open_dataset = open_dataset


def remove_agreements(db, agreements: List[Agreement]):
    for agreement in agreements:
        agreement_repository = AgreementRepository(db)
        agreement_repository.remove(agreement)


def get_agreements_from_api(context, agreement):
    """Abstracted so both account and single sign on APIs use in their tests"""
    if agreement == PRIVACY_POLICY:
        url = '/api/agreement/privacy-policy'
    elif agreement == TERMS_OF_USE:
        url = '/api/agreement/terms-of-use'
    else:
        raise ValueError('invalid agreement type')

    context.response = context.client.get(url)


def validate_agreement_response(context, agreement):
    response_data = json.loads(context.response.data)
    if agreement == PRIVACY_POLICY:
        expected_response = asdict(context.privacy_policy)
    elif agreement == TERMS_OF_USE:
        expected_response = asdict(context.terms_of_use)
    else:
        raise ValueError('invalid agreement type')

    del(expected_response['effective_date'])
    assert_that(response_data, equal_to(expected_response))
