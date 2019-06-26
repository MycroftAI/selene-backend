from selene.data.device import DeviceRepository, TextToSpeech


def _build_voice():
    return TextToSpeech(
        setting_name='selene_test_voice',
        display_name='Selene Test Voice',
        engine='mimic'
    )


def add_text_to_speech(db):
    voice = _build_voice()
    device_repository = DeviceRepository(db)
    voice.id = device_repository.add_text_to_speech(voice)

    return voice


def remove_text_to_speech(db, voice):
    device_repository = DeviceRepository(db)
    device_repository.remove_text_to_speech(voice.id)
