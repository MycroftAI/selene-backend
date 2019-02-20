from datetime import date, timedelta
from os import path
from logging import getLogger

from psycopg2.extras import DateRange

from selene.util.db import (
    Cursor,
    DatabaseRequest,
    get_sql_from_file,
    use_transaction
)
from ..entity.agreement import Agreement

SQL_DIR = path.join(path.dirname(__file__), 'sql')

_log = getLogger('selene.data.account')


class AgreementRepository(object):
    def __init__(self, db):
        self.db = db
        self.cursor = Cursor(db)
        self.skip_no_agreement_error = False

    @use_transaction
    def add(self, agreement: Agreement) -> str:
        self.skip_no_agreement_error = True
        expire_date = agreement.effective_date + timedelta(days=1)
        self.expire(agreement, expire_date)
        content_id = self._add_agreement_content(agreement.content)
        agreement_id = self._add_agreement(agreement, content_id)

        return agreement_id

    def _add_agreement_content(self, content):
        large_object = self.db.lobject(0, 'b')
        large_object.write(content)

        return large_object.oid

    def _add_agreement(self, agreement: Agreement, content_id: int) -> str:
        date_range = DateRange(agreement.effective_date, None)
        request = DatabaseRequest(
            sql=get_sql_from_file(path.join(SQL_DIR, 'add_agreement.sql')),
            args=dict(
                agreement_type=agreement.type,
                version=agreement.version,
                date_range=date_range,
                content_id=content_id
            )
        )
        result = self.cursor.insert_returning(request)
        _log.info('added {} agreement version {} starting {}'.format(
            agreement.type,
            agreement.version,
            agreement.effective_date
        ))

        return result['id']

    def expire(self, agreement: Agreement, expire_date: date):
        active_agreement = self.get_active_for_type(agreement.type)
        if active_agreement is not None:
            date_range = DateRange(active_agreement.effective_date, expire_date)
            request = DatabaseRequest(
                sql=get_sql_from_file(
                    path.join(SQL_DIR, 'expire_agreement.sql')
                ),
                args=dict(agreement_type=agreement.type, date_range=date_range)
            )
            self.cursor.update(request)
            log_msg = 'set expire date of active {} agreement to {}'
            _log.info(log_msg.format(agreement.type, expire_date))
        else:
            _log.info('no active {} agreement to expire'.format(agreement.type))

    @use_transaction
    def remove(self, agreement: Agreement, testing=False):
        """AGREEMENTS SHOULD NEVER BE REMOVED!  ONLY USE IN TEST CODE!"""
        if testing:
            content_id = self._get_agreement_content_id(agreement.id)
            large_object = self.db.lobject(content_id)
            large_object.unlink()
            request = DatabaseRequest(
                sql=get_sql_from_file(
                    path.join(SQL_DIR, 'delete_agreement.sql')
                ),
                args=dict(agreement_id=agreement.id)
            )
            self.cursor.delete(request)
            log_msg = 'deleted {} agreement version {}'
            _log.info(log_msg.format(agreement.type, agreement.version))

    def _get_agreement_content_id(self, agreement_id: str) -> int:
        request = DatabaseRequest(
            sql=get_sql_from_file(
                path.join(SQL_DIR, 'get_agreement_content_id.sql')
            ),
            args=dict(agreement_id=agreement_id)
        )
        result = self.cursor.select_one(request)

        return result['content_id']

    @use_transaction
    def get_active(self):
        agreements = []
        request = DatabaseRequest(
            sql=get_sql_from_file(
                path.join(SQL_DIR, 'get_current_agreements.sql')
            )
        )
        for row in self.cursor.select_all(request):
            content = self._get_agreement_content(row['content_id'])
            agreements.append(
                Agreement(
                    id=row['id'],
                    type=row['agreement'],
                    version=row['version'],
                    content=content,
                    effective_date=row['effective_date']
                )
            )

        if not agreements and not self.skip_no_agreement_error:
            _log.error('no agreements found with effective date of today')

        return agreements

    def get_active_for_type(self, agreement_type):
        agreement = None
        for active_agreement in self.get_active():
            if active_agreement.type == agreement_type:
                agreement = active_agreement

        return agreement

    def _get_agreement_content(self, content_id):
        large_object = self.db.lobject(content_id, 'r')
        return large_object.read()
