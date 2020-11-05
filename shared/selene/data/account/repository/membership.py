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

from selene.data.account import AccountMembership
from ..entity.membership import Membership
from ...repository_base import RepositoryBase

MONTHLY_MEMBERSHIP = 'Monthly Membership'
YEARLY_MEMBERSHIP = 'Yearly Membership'


class MembershipRepository(RepositoryBase):
    def __init__(self, db):
        """
        Initialize database.

        Args:
            self: (todo): write your description
            db: (todo): write your description
        """
        super(MembershipRepository, self).__init__(db, __file__)

    def get_membership_types(self):
        """
        Returns a list of membership types.

        Args:
            self: (todo): write your description
        """
        db_request = self._build_db_request(
            sql_file_name='get_membership_types.sql'
        )
        db_result = self.cursor.select_all(db_request)

        return [Membership(**row) for row in db_result]

    def get_membership_by_type(self, membership_type: str):
        """
        Gets membership types of the specified type

        Args:
            self: (todo): write your description
            membership_type: (str): write your description
        """
        db_request = self._build_db_request(
            sql_file_name='get_membership_by_type.sql',
            args=dict(type=membership_type)
        )
        db_result = self.cursor.select_one(db_request)
        return Membership(**db_result)

    def add(self, membership: Membership):
        """
        Add a membership to the group.

        Args:
            self: (todo): write your description
            membership: (todo): write your description
        """
        db_request = self._build_db_request(
            'add_membership.sql',
            args=dict(
                membership_type=membership.type,
                rate=membership.rate,
                rate_period=membership.rate_period
            )
        )
        result = self.cursor.insert_returning(db_request)

        return result['id']

    def remove(self, membership: Membership):
        """
        Removes the membership from the group.

        Args:
            self: (todo): write your description
            membership: (todo): write your description
        """
        db_request = self._build_db_request(
            sql_file_name='delete_membership.sql',
            args=dict(membership_id=membership.id)
        )
        self.cursor.delete(db_request)
