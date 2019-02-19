"""API endpoint to return the a logged-in user's profile"""
from dataclasses import asdict
from datetime import date
from http import HTTPStatus

from flask import json, jsonify
from schematics import Model
from schematics.exceptions import ValidationError
from schematics.types import BooleanType, EmailType, ModelType, StringType

from selene.data.account import (
    Account,
    AccountAgreement,
    AccountRepository,
    AccountSubscription,
    PRIVACY_POLICY,
    TERMS_OF_USE
)
from selene.util.db import get_db_connection
from ..base_endpoint import SeleneEndpoint

membeship_types = {
    'MONTHLY SUPPORTER': 'Monthly Supporter',
    'YEARLY SUPPORTER': 'Yearly Supporter',
    'MAYBE LATER': 'Maybe Later'
}


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
        required=True,
        choices=('MONTHLY SUPPORTER', 'YEARLY SUPPORTER', 'MAYBE LATER')
    )
    stripe_customer_id = StringType()

    # def validate_stripe_customer_id(self, data, value):
    #     if data['membership'] != 'Maybe Later':
    #         if not data['stripe_customer_id']:
    #             raise ValidationError('Membership requires a stripe ID')
    #     return value


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
        response_data = asdict(self.account)
        del (response_data['refresh_tokens'])
        self.response = response_data, HTTPStatus.OK

        return self.response

    def post(self):
        self.request_data = json.loads(self.request.data)
        self._validate_request()
        email_address, password = self._determine_login_method()
        self._add_account(email_address, password)

        return jsonify('Account added successfully'), HTTPStatus.OK

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
                stripe_customer_id=support_data.get('stripeCustomerId')
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
        membership_type = membeship_types[
            self.request_data['support']['membership']
        ]
        account = Account(
            email_address=email_address,
            username=self.request_data['username'],
            agreements=[
                AccountAgreement(type=PRIVACY_POLICY, accept_date=date.today()),
                AccountAgreement(type=TERMS_OF_USE, accept_date=date.today())
            ],
            subscription=AccountSubscription(
                type=membership_type,
                start_date=date.today(),
                stripe_customer_id=self.request_data['support']['stripeCustomerId']
            )
        )
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            acct_repository = AccountRepository(db)
            acct_repository.add(
                account,
                password=password
            )
