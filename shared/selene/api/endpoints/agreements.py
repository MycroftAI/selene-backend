"""API endpoint to return the contents of an agreement."""
from dataclasses import asdict
from http import HTTPStatus

from selene.data.account import AgreementRepository
from selene.util.db import connect_to_db
from ..base_endpoint import SeleneEndpoint


class AgreementsEndpoint(SeleneEndpoint):
    authentication_required = False
    agreement_types = {
        'terms-of-use': 'Terms of Use',
        'privacy-policy': 'Privacy Policy'
    }

    def get(self, agreement_type):
        """Process HTTP GET request for an agreement."""
        db = connect_to_db(self.config['DB_CONNECTION_CONFIG'])
        agreement_repository = AgreementRepository(db)
        agreement = agreement_repository.get_active_for_type(
            self.agreement_types[agreement_type]
        )
        if agreement is not None:
            agreement = asdict(agreement)
            del(agreement['effective_date'])
        self.response = agreement, HTTPStatus.OK

        return self.response
