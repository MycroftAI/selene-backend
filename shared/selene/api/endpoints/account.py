"""API endpoint to return the a logged-in user's profile"""
import os
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
    PRIVACY_POLICY,
    TERMS_OF_USE,
    MembershipRepository)
from selene.util.auth import (
    get_facebook_account_email,
    get_google_account_email
)
from selene.util.db import get_db_connection
from selene.util.payment import (
    cancel_stripe_subscription,
    create_stripe_account,
    create_stripe_subscription
)
from ..base_endpoint import SeleneEndpoint

MONTHLY_MEMBERSHIP = 'Monthly Membership'
YEARLY_MEMBERSHIP = 'Yearly Membership'
STRIPE_PAYMENT = 'Stripe'


def agreement_accepted(value):
    if not value:
        raise ValidationError('agreement not accepted')


class Login(Model):
    federated_platform = StringType(choices=['Facebook', 'Google'])
    federated_token = StringType()
    user_entered_email = EmailType()
    password = StringType()

    def validate_user_entered_email(self, data, value):
        if data['federated_token'] is None:
            if value is None:
                raise ValidationError(
                    'either a federated login or an email address is required'
                )

    def validate_password(self, data, value):
        if data['user_entered_email'] is not None:
            if value is None:
                raise ValidationError(
                    'email address must be accompanied by a password'
                )


class Support(Model):
    open_dataset = BooleanType(required=True)
    membership = StringType(
        choices=(MONTHLY_MEMBERSHIP, YEARLY_MEMBERSHIP)
    )
    payment_method = StringType(choices=[STRIPE_PAYMENT])
    payment_token = StringType()


class UpdateMembershipRequest(Model):
    new_membership = BooleanType(required=True)
    membership_type = StringType(
        choices=(MONTHLY_MEMBERSHIP, YEARLY_MEMBERSHIP)
    )
    payment_method = StringType(choices=[STRIPE_PAYMENT])
    payment_token = StringType()

    def validate_membership_type(self, data, value):
        if data['new_membership'] and value is None:
            raise ValidationError('new memberships require a membership type')

    def validate_payment_method(self, data, value):
        if data['new_membership'] and value is None:
            raise ValidationError('new memberships require a payment method')

    def validate_payment_token(self, data, value):
        if data['new_membership'] and value is None:
            raise ValidationError('payment token required for new memberships')


class AddAccountRequest(Model):
    username = StringType(required=True)
    privacy_policy = BooleanType(required=True, validators=[agreement_accepted])
    terms_of_use = BooleanType(required=True, validators=[agreement_accepted])
    login = ModelType(Login)
    support = ModelType(Support)


class AccountEndpoint(SeleneEndpoint):
    """Retrieve information about the user based on their UUID"""
    def __init__(self):
        super(AccountEndpoint, self).__init__()
        self.request_data = None
        stripe.api_key = os.environ['STRIPE_PRIVATE_KEY']

    def get(self):
        """Process HTTP GET request for an account."""
        self._authenticate()
        response_data = self._build_response_data()
        self.response = response_data, HTTPStatus.OK

        return self.response

    def _build_response_data(self):
        response_data = asdict(self.account)
        for agreement in response_data['agreements']:
            agreement_date = self._format_agreement_date(agreement)
            agreement['accept_date'] = agreement_date
        if response_data['membership'] is None:
            response_data['membership'] = None
        else:
            membership_duration = self._format_membership_duration(response_data)
            response_data['membership']['duration'] = membership_duration
            del (response_data['membership']['start_date'])
        del (response_data['refresh_tokens'])

        return response_data

    @staticmethod
    def _format_agreement_date(agreement):
        agreement_date = datetime.strptime(agreement['accept_date'], '%Y-%m-%d')
        formatted_agreement_date = agreement_date.strftime('%B %d, %Y')

        return formatted_agreement_date

    @staticmethod
    def _format_membership_duration(response_data):
        membership_start = datetime.strptime(
            response_data['membership']['start_date'],
            '%Y-%m-%d'
        )
        one_year = timedelta(days=365)
        one_month = timedelta(days=30)
        duration = date.today() - membership_start.date()
        years, remaining_duration = divmod(duration, one_year)
        months, _ = divmod(remaining_duration, one_month)
        membership_duration = []
        if years:
            membership_duration.append('{} years'.format(years))
        if months:
            membership_duration.append(' {} months'.format(str(months)))

        return ' '.join(membership_duration) if membership_duration else None

    def post(self):
        self.request_data = json.loads(self.request.data)
        self._validate_post_request()
        email_address, password = self._determine_login_method()
        self._add_account(email_address, password)
        return jsonify('Account added successfully'), HTTPStatus.OK

    def _validate_post_request(self):
        add_request = AddAccountRequest(dict(
            username=self.request_data.get('username'),
            privacy_policy=self.request_data.get('privacyPolicy'),
            terms_of_use=self.request_data.get('termsOfUse'),
            login=self._build_login_schematic(),
            support=self._build_support_schematic()
        ))
        add_request.validate()

    def _build_login_schematic(self) -> Login:
        login = None
        login_data = self.request_data['login']
        if login_data is not None:
            login = Login(dict(
                federated_platform=login_data.get('federatedPlatform'),
                federated_token=login_data.get('federatedToken'),
                user_entered_email=login_data.get('userEnteredEmail'),
                password=login_data.get('password')
            ))

        return login

    def _build_support_schematic(self):
        support = None
        support_data = self.request_data.get('support')
        if support_data is not None:
            support = Support(dict(
                open_dataset=support_data.get('openDataset'),
                membership=support_data.get('membership'),
                payment_method=support_data.get('paymentMethod'),
                payment_token=support_data.get('paymentToken')
            ))

        return support

    def _determine_login_method(self):
        login_data = self.request_data['login']
        password = None
        if login_data['federatedPlatform'] == 'Facebook':
            email_address = get_facebook_account_email(
                login_data['federatedToken']
            )
        elif login_data['federatedPlatform'] == 'Google':
            email_address = get_google_account_email(
                login_data['federatedToken']
            )
        else:
            email_address = login_data['userEnteredEmail']
            password = login_data['password']

        return email_address, password

    def _add_account(self, email_address, password):
        account_membership = self._build_account_membership()
        account = Account(
            email_address=email_address,
            username=self.request_data['username'],
            agreements=[
                AccountAgreement(type=PRIVACY_POLICY, accept_date=date.today()),
                AccountAgreement(type=TERMS_OF_USE, accept_date=date.today())
            ],
            membership=account_membership
        )
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            acct_repository = AccountRepository(db)
            acct_repository.add(
                account,
                password=password
            )

    def _build_account_membership(self):
        membership_type = self.request_data['support']['membership']
        membership = None
        if membership_type is not None:
            payment_account_id = create_stripe_account(
                self.request_data['support']['paymentToken'],
                self.request_data['login']['userEnteredEmail']

            )
            stripe_plan = self._get_stripe_plan(membership_type)
            subscription_id = create_stripe_subscription(
                payment_account_id,
                stripe_plan
            )

            membership = AccountMembership(
                type=membership_type,
                start_date=date.today(),
                payment_method=self.request_data['support']['paymentMethod'],
                payment_account_id=payment_account_id,
                payment_id=subscription_id
            )

        return membership

    def patch(self):
        self._authenticate()
        self.request_data = json.loads(self.request.data)
        requested_updates, errors = self._validate_patch_request()
        if errors:
            response_data = dict(errors=errors)
            response_status = HTTPStatus.BAD_REQUEST
        else:
            self._apply_updates(requested_updates)
            response_data = ''
            response_status = HTTPStatus.NO_CONTENT

        return response_data, response_status

    def _validate_patch_request(self):
        errors = []
        requested_updates = []
        for key, value in self.request_data.items():
            if key == 'membership':
                valid_values = self._validate_membership_update_request(value)
                requested_updates.append(valid_values)
            else:
                errors.append('update of {} not supported'.format(key))

        return requested_updates, errors

    def _validate_membership_update_request(self, value):
        validator = UpdateMembershipRequest()
        validator.new_membership = value['newMembership']
        validator.membership_type = value['membershipType']
        validator.payment_token = value.get('paymentToken')
        validator.payment_method = value.get('paymentMethod')
        validator.validate()

        return validator

    def _apply_updates(self, requested_updates):
        for requested_update in requested_updates:
            if isinstance(requested_update, UpdateMembershipRequest):
                self._update_membership(requested_update.to_native())

    def _get_stripe_plan(self, plan):
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            membership_repository = MembershipRepository(db)
            membership = membership_repository.get_membership_by_type(plan)

        return membership.stripe_plan

    def _update_membership(self, membership_change):
        active_membership = self._get_active_membership()
        if membership_change['membership_type'] is None:
            self._cancel_membership(active_membership)
        elif membership_change['new_membership']:
            if active_membership is None:
                self._add_membership(membership_change, active_membership)
            else:
                raise ValidationError(
                    'new membership requested for account with active '
                    'membership'
                )
        else:
            if active_membership is None:
                raise ValidationError(
                    'membership change requested for account with no '
                    'active membership'
                )
            else:
                self._cancel_membership(active_membership)
                self._add_membership(membership_change, active_membership)

    def _get_active_membership(self):
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            membership_repo = MembershipRepository(db)
            active_membership = membership_repo.get_active_account_membership(
                self.account.id
            )

        return active_membership

    def _add_membership(self, membership_change, active_membership):
        if active_membership is None:
            payment_account_id = create_stripe_account(
                membership_change['payment_token'],
                self.account.email_address
            )
        else:
            payment_account_id = active_membership.payment_account_id
        stripe_plan = self._get_stripe_plan(
            membership_change['membership_type']
        )
        payment_id = create_stripe_subscription(payment_account_id, stripe_plan)

        new_membership = AccountMembership(
            start_date=date.today(),
            payment_method=STRIPE_PAYMENT,
            payment_account_id=payment_account_id,
            payment_id=payment_id,
            type=membership_change['membership_type']
        )

        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            account_repository = AccountRepository(db)
            account_repository.add_membership(self.account.id, new_membership)

    def _cancel_membership(self, active_membership):
        cancel_stripe_subscription(active_membership.payment_id)
        active_membership.end_date = datetime.utcnow()
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            membership_repository = MembershipRepository(db)
            membership_repository.finish_membership(active_membership)

    def delete(self):
        self._authenticate()
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            account_repository = AccountRepository(db)
            account_repository.remove(self.account)

        return '', HTTPStatus.NO_CONTENT
