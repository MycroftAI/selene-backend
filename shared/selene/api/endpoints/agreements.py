"""API endpoint to return the contents of an agreement."""
from dataclasses import asdict
from http import HTTPStatus

from selene.data.account import AgreementRepository
from selene.util.db import get_db_connection
from ..base_endpoint import SeleneEndpoint


class AgreementsEndpoint(SeleneEndpoint):
    authentication_required = False
    agreement_types = {
        'terms-of-use': 'Terms of Use',
        'privacy-policy': 'Privacy Policy'
    }

    def get(self, agreement_type):
        """Process HTTP GET request for an agreement."""
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            agreement_repository = AgreementRepository(db)
            agreement = agreement_repository.get_active_for_type(
                self.agreement_types[agreement_type]
            )
            if agreement is not None:
                agreement = asdict(agreement)
                del(agreement['effective_date'])
            self.response = agreement, HTTPStatus.OK

        return self.response
