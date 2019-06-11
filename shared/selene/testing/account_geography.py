from selene.data.device import Geography, GeographyRepository


def add_account_geography(db, account, **overrides):
    geography = Geography(
        country=overrides.get('country') or 'United States',
        region=overrides.get('region') or 'Missouri',
        city=overrides.get('city') or 'Kansas City',
        time_zone=overrides.get('time_zone') or 'America/Chicago'
    )
    geo_repository = GeographyRepository(db, account.id)
    account_geography_id = geo_repository.add(geography)

    return account_geography_id
