from selene.data.device import DeviceRepository, WakeWord


def _build_wake_word():
    return WakeWord(
        setting_name='selene_test_wake_word',
        display_name='Selene Test Wake Word',
        engine='precise'
    )


def add_wake_word(db):
    wake_word = _build_wake_word()
    device_repository = DeviceRepository(db)
    wake_word.id = device_repository.add_wake_word(wake_word)

    return wake_word


def remove_wake_word(db, wake_word):
    device_repository = DeviceRepository(db)
    device_repository.remove_wake_word(wake_word.id)
