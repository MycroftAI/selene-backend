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

"""API endpoint to return the a logged-in user's profile"""
import os
from binascii import a2b_base64
from dataclasses import asdict
from datetime import date, datetime, timedelta
from http import HTTPStatus

import stripe
from flask import json, jsonify
from schematics import Model
from schematics.exceptions import ValidationError
from schematics.types import BooleanType, EmailType, ModelType, StringType

from selene.data.account import (
    Account,
    AccountAgreement,
    AccountRepository,
    AccountMembership,
    OPEN_DATASET,
    PRIVACY_POLICY,
    TERMS_OF_USE,
    MembershipRepository,
)
from selene.data.metric import AccountActivityRepository
from selene.util.auth import (
    get_facebook_account_email,
    get_github_account_email,
    get_google_account_email,
)
from selene.util.cache import SeleneCache
from selene.util.payment import (
    cancel_stripe_subscription,
    create_stripe_account,
    create_stripe_subscription,
)
from ..base_endpoint import SeleneEndpoint
from ..etag import ETagManager

MONTHLY_MEMBERSHIP = "Monthly Membership"
YEARLY_MEMBERSHIP = "Yearly Membership"
STRIPE_PAYMENT = "Stripe"


def agreement_accepted(value):
    """
    Validate that the given value.

    Args:
        value: (todo): write your description
    """
    if not value:
        raise ValidationError("agreement not accepted")


class Login(Model):
    federated_platform = StringType(choices=["Facebook", "Google", "GitHub"])
    federated_token = StringType()
    email = EmailType()
    password = StringType()

    def validate_email(self, data, value):
        """
        Validate value is a valid email address.

        Args:
            self: (todo): write your description
            data: (array): write your description
            value: (todo): write your description
        """
        if data["federated_token"] is None:
            if value is None:
                raise ValidationError(
                    "either a federated login or an email address is required"
                )

    def validate_password(self, data, value):
        """
        Validate password.

        Args:
            self: (todo): write your description
            data: (array): write your description
            value: (str): write your description
        """
        if data["email"] is not None:
            if value is None:
                raise ValidationError("email address must be accompanied by a password")


class Support(Model):
    open_dataset = BooleanType(required=True)
    membership = StringType(choices=(MONTHLY_MEMBERSHIP, YEARLY_MEMBERSHIP))
    payment_method = StringType(choices=[STRIPE_PAYMENT])
    payment_token = StringType()


class UpdateMembershipRequest(Model):
    new_membership = BooleanType(required=True)
    membership_type = StringType(choices=(MONTHLY_MEMBERSHIP, YEARLY_MEMBERSHIP))
    payment_method = StringType(choices=[STRIPE_PAYMENT])
    payment_token = StringType()

    def validate_membership_type(self, data, value):
        """
        Validate the membership type.

        Args:
            self: (todo): write your description
            data: (array): write your description
            value: (todo): write your description
        """
        if data["new_membership"] and value is None:
            raise ValidationError("new memberships require a membership type")

    def validate_payment_method(self, data, value):
        """
        Validate payment method.

        Args:
            self: (todo): write your description
            data: (array): write your description
            value: (str): write your description
        """
        if data["new_membership"] and value is None:
            raise ValidationError("new memberships require a payment method")

    def validate_payment_token(self, data, value):
        """
        Validate payment token.

        Args:
            self: (todo): write your description
            data: (todo): write your description
            value: (str): write your description
        """
        if data["new_membership"] and value is None:
            raise ValidationError("payment token required for new memberships")


class AddAccountRequest(Model):
    privacy_policy = BooleanType(required=True, validators=[agreement_accepted])
    terms_of_use = BooleanType(required=True, validators=[agreement_accepted])
    login = ModelType(Login)


class AccountEndpoint(SeleneEndpoint):
    """Retrieve information about the user based on their UUID"""

    _account_repository = None
    _account_activity_repository = None

    def __init__(self):
        """
        Initialize the request.

        Args:
            self: (todo): write your description
        """
        super(AccountEndpoint, self).__init__()
        self.request_data = None

    @property
    def account_repository(self):
        """
        Returns the repository repository.

        Args:
            self: (todo): write your description
        """
        if self._account_repository is None:
            self._account_repository = AccountRepository(self.db)

        return self._account_repository

    @property
    def account_activity_repository(self):
        """
        Gets the activity activity list of the account.

        Args:
            self: (todo): write your description
        """
        if self._account_activity_repository is None:
            self._account_activity_repository = AccountActivityRepository(self.db)

        return self._account_activity_repository

    def get(self):
        """Process HTTP GET request for an account."""
        self._authenticate()
        response_data = self._build_response_data()
        self.response = response_data, HTTPStatus.OK

        return self.response

    def _build_response_data(self):
        """
        Builds the response data dictionary for the analysis.

        Args:
            self: (todo): write your description
        """
        response_data = asdict(self.account)
        for agreement in response_data["agreements"]:
            agreement_date = self._format_agreement_date(agreement)
            agreement["accept_date"] = agreement_date
        if response_data["membership"] is None:
            response_data["membership"] = None
        else:
            membership_duration = self._format_membership_duration(response_data)
            response_data["membership"]["duration"] = membership_duration
            del response_data["membership"]["start_date"]

        return response_data

    @staticmethod
    def _format_agreement_date(agreement):
        """
        Format the agreement date.

        Args:
            agreement: (str): write your description
        """
        agreement_date = datetime.strptime(agreement["accept_date"], "%Y-%m-%d")
        formatted_agreement_date = agreement_date.strftime("%B %d, %Y")

        return formatted_agreement_date

    @staticmethod
    def _format_membership_duration(response_data):
        """
        Formats the duration.

        Args:
            response_data: (bool): write your description
        """
        membership_start = datetime.strptime(
            response_data["membership"]["start_date"], "%Y-%m-%d"
        )
        one_year = timedelta(days=365)
        one_month = timedelta(days=30)
        duration = datetime.utcnow().date() - membership_start.date()
        years, remaining_duration = divmod(duration, one_year)
        months, _ = divmod(remaining_duration, one_month)
        membership_duration = []
        if years:
            membership_duration.append("{} years".format(years))
        if months:
            membership_duration.append(" {} months".format(str(months)))

        return " ".join(membership_duration) if membership_duration else None

    def post(self):
        """
        Creates request

        Args:
            self: (todo): write your description
        """
        self.request_data = json.loads(self.request.data)
        self._validate_post_request()
        email_address, password = self._determine_login_method()
        self._add_account(email_address, password)
        return jsonify("Account added successfully"), HTTPStatus.OK

    def _validate_post_request(self):
        """
        Validate the login request.

        Args:
            self: (todo): write your description
        """
        add_request = AddAccountRequest(
            dict(
                privacy_policy=self.request_data.get("privacyPolicy"),
                terms_of_use=self.request_data.get("termsOfUse"),
                login=self._build_login_schematic(),
            )
        )
        add_request.validate()

        self.request_data = add_request.to_native()

    def _build_login_schematic(self) -> Login:
        """
        Build login login request.

        Args:
            self: (todo): write your description
        """
        login = None
        login_data = self.request.json.get("login")
        if login_data is not None:
            email = login_data.get("email")
            if email is not None:
                email = a2b_base64(email).decode()
            password = login_data.get("password")
            if password is not None:
                password = a2b_base64(password).decode()
            login = Login(
                dict(
                    federated_platform=login_data.get("federatedPlatform"),
                    federated_token=login_data.get("federatedToken"),
                    email=email,
                    password=password,
                )
            )

        return login

    def _determine_login_method(self):
        """
        Determine the login method.

        Args:
            self: (todo): write your description
        """
        login_data = self.request_data["login"]
        password = None
        if login_data["federated_platform"] == "Facebook":
            email_address = get_facebook_account_email(login_data["federated_token"])
        elif login_data["federated_platform"] == "Google":
            email_address = get_google_account_email(login_data["federated_token"])
        elif login_data["federated_platform"] == "GitHub":
            email_address = get_github_account_email(login_data.args["federated_token"])
        else:
            email_address = login_data["email"]
            password = login_data["password"]

        return email_address, password

    def _add_account(self, email_address, password):
        """
        Add a new account.

        Args:
            self: (todo): write your description
            email_address: (str): write your description
            password: (str): write your description
        """
        account = Account(
            email_address=email_address,
            agreements=[
                AccountAgreement(type=PRIVACY_POLICY, accept_date=date.today()),
                AccountAgreement(type=TERMS_OF_USE, accept_date=date.today()),
            ],
        )
        self.account_repository.add(account, password=password)
        self.account_activity_repository.increment_accounts_added()

    def patch(self):
        """
        Authenticates the device.

        Args:
            self: (todo): write your description
        """
        self._authenticate()
        errors = self._update_account()
        if errors:
            response_data = dict(errors=errors)
            response_status = HTTPStatus.BAD_REQUEST
        else:
            self._expire_device_setting_cache()
            response_data = ""
            response_status = HTTPStatus.NO_CONTENT

        return response_data, response_status

    def _expire_device_setting_cache(self):
        """
        Expire the device to be used in the device.

        Args:
            self: (todo): write your description
        """
        cache = SeleneCache()
        etag_manager = ETagManager(cache, self.config)
        etag_manager.expire_device_setting_etag_by_account_id(self.account.id)

    def _update_account(self):
        """
        Updates members.

        Args:
            self: (todo): write your description
        """
        errors = []
        for key, value in self.request.json.items():
            if key == "membership":
                valid_values = self._validate_membership_update_request(value)
                self._update_membership(valid_values.to_native())
            elif key == "username":
                self._update_username(value)
            elif key == "openDataset":
                self._update_open_dataset_agreement(value)
            else:
                errors.append("update of {} not supported".format(key))

        return errors

    def _validate_membership_update_request(self, value):
        """
        Validate the membership membership.

        Args:
            self: (todo): write your description
            value: (dict): write your description
        """
        validator = UpdateMembershipRequest()
        validator.new_membership = value["newMembership"]
        validator.membership_type = value["membershipType"]
        validator.payment_token = value.get("paymentToken")
        validator.payment_method = value.get("paymentMethod")
        validator.validate()

        return validator

    def _update_membership(self, membership_change):
        """
        Updates the membership membership.

        Args:
            self: (todo): write your description
            membership_change: (todo): write your description
        """
        stripe.api_key = os.environ["STRIPE_PRIVATE_KEY"]
        active_membership = self._get_active_membership()
        if membership_change["membership_type"] is None:
            self._cancel_membership(active_membership)
            self.account_activity_repository.increment_members_expired()
        elif membership_change["new_membership"]:
            if active_membership is None:
                self._add_membership(membership_change, active_membership)
                self.account_activity_repository.increment_members_added()
            else:
                raise ValidationError(
                    "new membership requested for account with active membership"
                )
        else:
            if active_membership is None:
                raise ValidationError(
                    "membership change requested for account with no "
                    "active membership"
                )
            else:
                self._cancel_membership(active_membership)
                self._add_membership(membership_change, active_membership)

    def _get_active_membership(self):
        """
        Returns the membership membership of the current user.

        Args:
            self: (todo): write your description
        """
        acct_repository = AccountRepository(self.db)
        active_membership = acct_repository.get_active_account_membership(
            self.account.id
        )

        return active_membership

    def _add_membership(self, membership_change, active_membership):
        """
        Add a new membership to the group.

        Args:
            self: (todo): write your description
            membership_change: (todo): write your description
            active_membership: (todo): write your description
        """
        if active_membership is None:
            payment_account_id = create_stripe_account(
                membership_change["payment_token"], self.account.email_address
            )
        else:
            payment_account_id = active_membership.payment_account_id
        stripe_plan = self._get_stripe_plan(membership_change["membership_type"])
        payment_id = create_stripe_subscription(payment_account_id, stripe_plan)

        new_membership = AccountMembership(
            start_date=date.today(),
            payment_method=STRIPE_PAYMENT,
            payment_account_id=payment_account_id,
            payment_id=payment_id,
            type=membership_change["membership_type"],
        )

        self.account_repository.add_membership(self.account.id, new_membership)

    def _get_stripe_plan(self, plan):
        """
        Gets the membership for the given plan.

        Args:
            self: (todo): write your description
            plan: (str): write your description
        """
        membership_repository = MembershipRepository(self.db)
        membership = membership_repository.get_membership_by_type(plan)

        return membership.stripe_plan

    def _cancel_membership(self, active_membership):
        """
        Cancel the membership of the given group.

        Args:
            self: (todo): write your description
            active_membership: (bool): write your description
        """
        cancel_stripe_subscription(active_membership.payment_id)
        active_membership.end_date = datetime.utcnow()
        account_repository = AccountRepository(self.db)
        account_repository.end_membership(active_membership)

    def _update_username(self, username):
        """
        Update the username of the account.

        Args:
            self: (todo): write your description
            username: (str): write your description
        """
        self.account_repository.update_username(self.account.id, username)

    def _update_open_dataset_agreement(self, opt_in: bool):
        """
        Updates the open accounts of the account.

        Args:
            self: (todo): write your description
            opt_in: (todo): write your description
        """
        if opt_in:
            agreement = AccountAgreement(type=OPEN_DATASET, accept_date=date.today())
            self.account_repository.add_agreement(self.account.id, agreement)
            self.account_activity_repository.increment_open_dataset_added()
        else:
            self.account_repository.expire_open_dataset_agreement(self.account.id)
            self.account_activity_repository.increment_open_dataset_deleted()

    def delete(self):
        """
        Deletes the member.

        Args:
            self: (todo): write your description
        """
        self._authenticate()
        self.account_repository.remove(self.account)
        self.account_activity_repository.increment_accounts_deleted()
        membership = self.account.membership
        if membership is not None:
            cancel_stripe_subscription(membership.payment_id)

        return "", HTTPStatus.NO_CONTENT
