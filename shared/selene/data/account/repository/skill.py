from typing import List

from selene.data.account.entity.skill import AccountSkill
from selene.data.repository_base import RepositoryBase


class AccountSkillRepository(RepositoryBase):
    def __init__(self, db, account_id):
        super(AccountSkillRepository, self).__init__(db, __file__)
        self.account_id = account_id

    def get_skills_for_account(self) -> List[AccountSkill]:
        db_request = self._build_db_request(
            sql_file_name='get_account_skills.sql',
            args=dict(account_id=self.account_id)
        )
        db_result = self.cursor.select_all(db_request)

        return [AccountSkill(**row) for row in db_result]
