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

import os

import stripe


def create_stripe_account(token: str, email: str):
    stripe.api_key = os.environ['STRIPE_PRIVATE_KEY']
    customer = stripe.Customer.create(source=token, email=email)
    return customer.id


def create_stripe_subscription(customer_id, plan):
    stripe.api_key = os.environ['STRIPE_PRIVATE_KEY']
    request = stripe.Subscription.create(
        customer=customer_id,
        items=[{'plan': plan}]
    )

    return request.id


def cancel_stripe_subscription(subscription_id):
    stripe.api_key = os.environ['STRIPE_PRIVATE_KEY']
    active_stripe_subscription = stripe.Subscription.retrieve(subscription_id)
    active_stripe_subscription.delete()
