from selene.data.geography import City, Country, Region, Timezone
from ..entity.default import AccountDefaults
from ..entity.text_to_speech import TextToSpeech
from ..entity.wake_word import WakeWord
from ...repository_base import RepositoryBase

defaults_dataclasses = dict(
    city=City,
    country=Country,
    region=Region,
    timezone=Timezone,
    voice=TextToSpeech,
    wake_word=WakeWord
)


class DefaultsRepository(RepositoryBase):
    def __init__(self, db, account_id):
        super(DefaultsRepository, self).__init__(db, __file__)
        self.account_id = account_id

    def add(self, defaults):
        db_request_args = dict(account_id=self.account_id)
        db_request_args.update(defaults)
        db_request_args['wake_word'] = db_request_args['wake_word']
        db_request = self._build_db_request(
            sql_file_name='add_account_defaults.sql',
            args=db_request_args
        )
        self.cursor.insert(db_request)

    def get_account_defaults(self):
        db_request = self._build_db_request(
            sql_file_name='get_account_defaults.sql',
            args=dict(account_id=self.account_id)
        )
        db_result = self.cursor.select_one(db_request)
        if db_result is None:
            defaults = None
        else:
            for key, dataclass in defaults_dataclasses.items():
                if db_result[key]['id'] is None:
                    db_result[key] = None
                else:
                    db_result[key] = dataclass(**db_result[key])
            defaults = AccountDefaults(**db_result)

        return defaults
