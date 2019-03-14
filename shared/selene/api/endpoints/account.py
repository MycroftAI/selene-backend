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
from selene.util.db import get_db_connection
from ..base_endpoint import SeleneEndpoint

MONTHLY_MEMBERSHIP = 'Monthly Membership'
YEARLY_MEMBERSHIP = 'Yearly Membership'
STRIPE_PAYMENT = 'Stripe'

stripe.api_key = os.environ['STRIPE_PRIVATE_KEY']


def agreement_accepted(value):
    if not value:
        raise ValidationError('agreement not accepted')


class Login(Model):
    federated_email = EmailType()
    user_entered_email = EmailType()
    password = StringType()

    def validate_user_entered_email(self, data, value):
        if data['federated_email'] is None:
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


class AddMembership(Model):
    membership = StringType(
        required=True,
        choices=(MONTHLY_MEMBERSHIP, YEARLY_MEMBERSHIP)
    )
    payment_method = StringType(required=True, choices=[STRIPE_PAYMENT])
    payment_token = StringType(required=True)


class UpdateMembership(Model):
    membership = StringType(
        required=True,
        choices=(MONTHLY_MEMBERSHIP, YEARLY_MEMBERSHIP)
    )


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
        self._validate_request()
        email_address, password = self._determine_login_method()
        self._add_account(email_address, password)
        return jsonify('Account added successfully'), HTTPStatus.OK

    def patch(self):
        self._authenticate()
        self.request_data = json.loads(self.request.data)
        self._update_support()
        return '', HTTPStatus.OK

    def _validate_request(self):
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
                federated_email=login_data.get('federatedEmail'),
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
        if login_data['federatedEmail'] is None:
            email_address = login_data['userEnteredEmail']
            password = login_data['password']
        else:
            email_address = login_data['federatedEmail']
            password = None

        return email_address, password

    def _add_account(self, email_address, password):
        membership_type = self.request_data['support']['membership']
        membership = None
        if membership_type is not None:
            payment_token = self.request_data['support']['paymentToken']
            email = self.request_data['login']['userEnteredEmail']
            plan = self._get_plan(membership_type).stripe_plan
            payment_account_id, start = self._create_stripe_subscription(None, payment_token, email, plan)
            membership = AccountMembership(
                type=membership_type,
                start_date=date.today(),
                payment_method=self.request_data['support']['paymentMethod'],
                payment_account_id=payment_account_id
            )
        account = Account(
            email_address=email_address,
            username=self.request_data['username'],
            agreements=[
                AccountAgreement(type=PRIVACY_POLICY, accept_date=date.today()),
                AccountAgreement(type=TERMS_OF_USE, accept_date=date.today())
            ],
            membership=membership
        )
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            acct_repository = AccountRepository(db)
            acct_repository.add(
                account,
                password=password
            )

    def _create_stripe_subscription(self, customer_id, token, user_email, plan):
        if customer_id is None:
            customer = stripe.Customer.create(source=token, email=user_email)
            customer_id = customer.id
        subscription = stripe.Subscription.create(customer=customer_id, items=[{'plan': plan}])

        # TODO: store subscription.id
        start = subscription.current_period_start
        start = date.fromtimestamp(start)
        return customer_id, start

    def _get_plan(self, plan):
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            return MembershipRepository(db).get_membership_by_type(plan)

    def _update_support(self):
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            membership_repository = MembershipRepository(db)
            active_membership = membership_repository.get_active_membership_by_account_id(self.account.id)
            if active_membership:
                active_membership.end_date = datetime.now()
                # TODO: use the subscription id to delete the membership on stripe
                membership_repository.finish_membership(active_membership)
                add_membership = UpdateMembership(self.request_data.get('support'))
                add_membership.validate()
                support = self.request_data['support']
                membership_type = support['membership']
                membership = self._get_plan(membership_type)
                stripe_id, start_date = self._create_stripe_subscription(
                    active_membership.payment_account_id,
                    None,
                    self.account.email_address,
                    membership.stripe_plan
                )
            else:
                add_membership = AddMembership(self.request_data.get('support'))
                add_membership.validate()
                support = self.request_data['support']
                membership_type = support['membership']
                token = support['payment_token']
                membership = self._get_plan(membership_type)
                stripe_id, start_date = self._create_stripe_subscription(
                    None,
                    token,
                    self.account.email_address,
                    membership.stripe_plan
                )

            new_membership = AccountMembership(
                start_date=start_date,
                payment_method=STRIPE_PAYMENT,
                payment_account_id=stripe_id,
                type=membership_type
            )
            AccountRepository(db).add_membership(self.account.id, new_membership)
