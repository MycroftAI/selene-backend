from selene.data.device import DeviceRepository


def add_device(db, account_id, geography_id):
    device = dict(
        name='Selene Test Device',
        pairing_code='ABC123',
        placement='kitchen',
        geography_id=geography_id,
        country='United States',
        region='Missouri',
        city='Kansas City',
        timezone='America/Chicago',
        wake_word='Selene Test Wake Word',
        voice='Selene Test Voice'
    )
    device_repository = DeviceRepository(db)
    device_id = device_repository.add(account_id, device)

    return device_id
