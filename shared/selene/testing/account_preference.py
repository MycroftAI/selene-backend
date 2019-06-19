from selene.data.device import AccountPreferences, PreferenceRepository


def add_account_preference(db, account_id):
    account_preferences = AccountPreferences(
        date_format='MM/DD/YYYY',
        time_format='12 Hour',
        measurement_system='Imperial'
    )
    preference_repo = PreferenceRepository(db, account_id)
    preference_repo.upsert(account_preferences)
