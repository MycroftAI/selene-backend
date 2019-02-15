"""API endpoint to return the a logged-in user's profile"""
from dataclasses import asdict
from datetime import date
from http import HTTPStatus

from flask import json
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
from .base_endpoint import SeleneEndpoint


def is_valid_membership(value):
    valid_values = ('Monthly Supporter', 'Yearly Supporter', 'Maybe Later')
    if value not in valid_values:
        raise ValidationError('Must be one of: ' + ', '.join(valid_values))


def agreement_accepted(value):
    if not value:
        raise ValidationError('agreement not accepted')


class Login(Model):
    federated_email = EmailType()
    user_entered_email = EmailType()
    password = StringType()


class Support(Model):
    open_dataset = BooleanType(required=True)
    membership = StringType(required=True, validators=[is_valid_membership])
    stripe_customer_id = StringType()

    def validate_stripe_customer_id(self, data, value):
        if data['membership'] != 'Maybe Later':
            if not data['stripe_customer_id']:
                raise ValidationError('Membership requires a stripe ID')
        return value


class AddAccountRequest(Model):
    display_name = StringType(required=True)
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
        if self.authenticated:
            response_data = asdict(self.account)
            del (response_data['refresh_tokens'])
            self.response = (response_data, HTTPStatus.OK)

        return self.response

    def post(self):
        self.request_data = json.loads(self.request.data)
        self._validate_request()
        email_address, password = self._determine_login_method()
        self._add_account(email_address, password)

    def _validate_request(self):
        try:
            add_request = AddAccountRequest(
                display_name=self.request.form['displayName'],
                privacy_policy=self.request.form['privacyPolicy'],
                terms_of_use=self.request.form['termsOfUse'],
                login=self._build_login_schematic(),
                support=self._build_support_schematic()
            )
            add_request.validate()
        except KeyError as ke:
            error_msg = (
                'post request missing an attribute necessary to create '
                'an account' + str(ke)
            )
            self.response = dict(error=error_msg), HTTPStatus.BAD_REQUEST
        except ValidationError as ve:
            error_msg = ve.messages
            self.response = dict(error=error_msg), HTTPStatus.BAD_REQUEST

    def _build_login_schematic(self) -> Login:
        login_data = self.request_data['login']
        login = Login(
            federated_email=login_data['federatedEmail'],
            user_entered_email=login_data['userEnteredEmail'],
            password=login_data['password']
        )

        return login

    def _build_support_schematic(self):
        support_data = self.request_data['support']
        support = Support(
            open_dataset=support_data['openDataset'],
            membership=support_data['membership'],
            stripe_customer_id=support_data['stripeCustomId']
        )

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
        account = Account(
            email_address=email_address,
            display_name=self.request_data['displayName'],
            agreements=[
                AccountAgreement(type=PRIVACY_POLICY, accept_date=date.today()),
                AccountAgreement(type=TERMS_OF_USE, accept_date=date.today())
            ],
            subscription=AccountSubscription(
                type=self.request_data['support']['membership'],
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
