from ..entity.preference import AccountPreferences
from ..entity.geography import Geography
from ..entity.text_to_speech import TextToSpeech
from ..entity.wake_word import WakeWord
from ...repository_base import RepositoryBase


class PreferenceRepository(RepositoryBase):
    def __init__(self, db, account_id):
        super(PreferenceRepository, self).__init__(db, __file__)
        self.account_id = account_id

    def get_account_preferences(self) -> AccountPreferences:
        db_request = self._build_db_request(
            sql_file_name='get_account_preferences.sql',
            args=dict(account_id=self.account_id)
        )

        db_result = self.cursor.select_one(db_request)
        if db_result is None:
            preferences = None
        else:
            if db_result['geography'] is None:
                db_result['geography'] = None
            else:
                db_result['geography'] = Geography(**db_result['geography'])
            if db_result['wake_word']['id'] is None:
                db_result['wake_word'] = None
            else:
                db_result['wake_word'] = WakeWord(**db_result['wake_word'])
            if db_result['voice']['id'] is None:
                db_result['voice'] = None
            else:
                db_result['voice'] = TextToSpeech(**db_result['voice'])
            preferences = AccountPreferences(**db_result)

        return preferences
