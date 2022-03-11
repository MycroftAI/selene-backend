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

"""API endpoint to return the contents of an agreement."""
from dataclasses import asdict
from http import HTTPStatus

from selene.data.account import AgreementRepository
from selene.util.db import connect_to_db
from ..base_endpoint import SeleneEndpoint


class AgreementsEndpoint(SeleneEndpoint):
    authentication_required = False
    agreement_types = {
        "terms-of-use": "Terms of Use",
        "privacy-policy": "Privacy Policy",
    }

    def get(self, agreement_type):
        """Process HTTP GET request for an agreement."""
        db = connect_to_db(self.config["DB_CONNECTION_CONFIG"])
        agreement_repository = AgreementRepository(db)
        agreement = agreement_repository.get_active_for_type(
            self.agreement_types[agreement_type]
        )
        if agreement is not None:
            agreement = asdict(agreement)
            del agreement["effective_date"]
        self.response = agreement, HTTPStatus.OK

        return self.response
