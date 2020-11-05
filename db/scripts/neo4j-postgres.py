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

import csv
import datetime
import json
import uuid
from collections import defaultdict

import time
from geopy.distance import distance
from psycopg2 import connect
from psycopg2.extras import execute_batch

users = {}
user_settings = {}
subscription = {}
devices = {}
user_devices = {}
skills = {}
skill_sections = {}
skill_fields = {}
skill_field_values = {}
device_to_skill = {}
skill_to_section = {}
section_to_field = {}
device_to_field = {}
locations = {}
timezones = {}
cities = {}
regions = {}
countries = {}
coordinates = {}
device_location = {}
hey_mycroft = str(uuid.uuid4())
christopher = str(uuid.uuid4())
ezra = str(uuid.uuid4())
jarvis = str(uuid.uuid4())

default_wake_words = {
    'hey mycroft': hey_mycroft,
    'christopher': christopher,
    'hey ezra': ezra,
    'hey jarvis': jarvis
}


def load_csv():
    """
    Load user config file.

    Args:
    """
    with open('users.csv') as user_csv:
        user_reader = csv.reader(user_csv)
        next(user_reader, None)
        for row in user_reader:
            # email, password
            users[row[0]] = {}
            users[row[0]]['email'] = row[1]
            users[row[0]]['password'] = row[2]
            users[row[0]]['terms'] = row[3]
            users[row[0]]['privacy'] = row[4]

    with open('user_settings.csv') as user_setting_csv:
        user_setting_reader = csv.reader(user_setting_csv)
        next(user_setting_reader, None)
        for row in user_setting_reader:
            user_settings[row[0]] = {}
            user_settings[row[0]]['date_format'] = row[1]
            user_settings[row[0]]['time_format'] = row[2]
            user_settings[row[0]]['measurement_system'] = row[3]
            user_settings[row[0]]['tts_type'] = row[4]
            user_settings[row[0]]['tts_voice'] = row[5]
            user_settings[row[0]]['wake_word'] = row[6]
            user_settings[row[0]]['sample_rate'] = row[7]
            user_settings[row[0]]['channels'] = row[8]
            user_settings[row[0]]['pronunciation'] = row[9]
            user_settings[row[0]]['threshold'] = row[10]
            user_settings[row[0]]['threshold_multiplier'] = row[11]
            user_settings[row[0]]['dynamic_energy_ratio'] = row[12]

    with open('subscription.csv') as subscription_csv:
        subscription_reader = csv.reader(subscription_csv)
        next(subscription_reader, None)
        for row in subscription_reader:
            subscription[row[0]] = {}
            subscription[row[0]]['stripe_customer_id'] = row[1]
            subscription[row[0]]['last_payment_ts'] = row[2]
            subscription[row[0]]['type'] = row[3]

    with open('devices.csv') as devices_csv:
        devices_reader = csv.reader(devices_csv)
        next(devices_reader, None)
        for row in devices_reader:
            devices[row[0]] = {}
            user_uuid = row[1]
            devices[row[0]]['user_uuid'] = row[1]
            devices[row[0]]['name'] = row[2]
            devices[row[0]]['description'] = row[3],
            devices[row[0]]['platform'] = row[4],
            devices[row[0]]['enclosure_version'] = row[5]
            devices[row[0]]['core_version'] = row[6]

            if user_uuid in user_devices:
                user_devices[user_uuid].append((row[0], row[2]))
            else:
                user_devices[user_uuid] = [(row[0], row[2])]

    with open('skill.csv') as skill_csv:
        skill_reader = csv.reader(skill_csv)
        next(skill_reader, None)
        for row in skill_reader:
            skill = row[0]
            skills[skill] = {}
            dev_uuid = row[1]
            skills[skill]['device_uuid'] = dev_uuid
            skills[skill]['name'] = row[2]
            skills[skill]['description'] = row[3]
            skills[skill]['identifier'] = row[4]
            if dev_uuid in device_to_skill:
                device_to_skill[dev_uuid].add(skill)
            else:
                device_to_skill[dev_uuid] = {skill}

    with open('skill_section.csv') as skill_section_csv:
        skill_section_reader = csv.reader(skill_section_csv)
        next(skill_section_reader, None)
        for row in skill_section_reader:
            section_uuid = row[0]
            skill_sections[section_uuid] = {}
            skill_uuid = row[1]
            skill_sections[section_uuid]['skill_uuid'] = skill_uuid
            skill_sections[section_uuid]['section'] = row[2]
            skill_sections[section_uuid]['display_order'] = row[3]
            if skill_uuid in skill_to_section:
                skill_to_section[skill_uuid].add(section_uuid)
            else:
                skill_to_section[skill_uuid] = {section_uuid}

    with open('skill_fields.csv') as skill_fields_csv:
        skill_fields_reader = csv.reader(skill_fields_csv)
        next(skill_fields_reader, None)
        for row in skill_fields_reader:
            field_uuid = row[0]
            skill_fields[field_uuid] = {}
            section_uuid = row[1]
            #skill_fields[field_uuid]['section_uuid'] = section_uuid
            skill_fields[field_uuid]['name'] = row[2]
            skill_fields[field_uuid]['type'] = row[3]
            skill_fields[field_uuid]['label'] = row[4]
            skill_fields[field_uuid]['hint'] = row[5]
            skill_fields[field_uuid]['placeholder'] = row[6]
            skill_fields[field_uuid]['hide'] = row[7]
            skill_fields[field_uuid]['options'] = row[8]
            #skill_fields[field_uuid]['order'] = row[9]
            if section_uuid in section_to_field:
                section_to_field[section_uuid].add(field_uuid)
            else:
                section_to_field[section_uuid] = {field_uuid}

    with open('skill_fields_values.csv') as skill_field_values_csv:
        skill_field_values_reader = csv.reader(skill_field_values_csv)
        next(skill_field_values_reader, None)
        for row in skill_field_values_reader:
            field_uuid = row[0]
            skill_field_values[field_uuid] = {}
            skill_field_values[field_uuid]['skill_uuid'] = row[1]
            device_uuid = row[2]
            skill_field_values[field_uuid]['device_uuid'] = device_uuid
            skill_field_values[field_uuid]['field_value'] = row[3]
            if device_uuid in device_to_field:
                device_to_field[device_uuid].add(field_uuid)
            else:
                device_to_field[device_uuid] = {field_uuid}

    with open('location.csv') as location_csv:
        location_reader = csv.reader(location_csv)
        next(location_reader, None)
        for row in location_reader:
            location_uuid = row[0]
            locations[location_uuid] = {}
            locations[location_uuid]['timezone'] = row[1]
            locations[location_uuid]['city'] = row[2]
            locations[location_uuid]['coordinate'] = row[3]

    with open('timezone.csv') as timezone_csv:
        timezone_reader = csv.reader(timezone_csv)
        next(timezone_reader, None)
        for row in timezone_reader:
            timezone_uuid = row[0]
            timezones[timezone_uuid] = {}
            timezones[timezone_uuid]['code'] = row[1]
            timezones[timezone_uuid]['name'] = row[2]

    with open('city.csv') as city_csv:
        city_reader = csv.reader(city_csv)
        next(city_reader, None)
        for row in city_reader:
            city_uuid = row[0]
            cities[city_uuid] = {}
            cities[city_uuid]['region'] = row[1]
            cities[city_uuid]['name'] = row[2]

    with open('region.csv') as region_csv:
        region_reader = csv.reader(region_csv)
        next(region_reader, None)
        for row in region_reader:
            region_uuid = row[0]
            regions[region_uuid] = {}
            regions[region_uuid]['country'] = row[1]
            regions[region_uuid]['name'] = row[2]
            regions[region_uuid]['code'] = row[3]

    with open('country.csv') as country_csv:
        country_reader = csv.reader(country_csv)
        next(country_reader, None)
        for row in country_reader:
            country_uuid = row[0]
            countries[country_uuid] = {}
            countries[country_uuid]['name'] = row[1]
            countries[country_uuid]['code'] = row[2]

    with open('coordinate.csv') as coordinate_csv:
        coordinate_reader = csv.reader(coordinate_csv)
        next(coordinate_reader, None)
        for row in coordinate_reader:
            coordinate_uuid = row[0]
            coordinates[coordinate_uuid] = {}
            coordinates[coordinate_uuid]['latitude'] = row[1]
            coordinates[coordinate_uuid]['longitude'] = row[2]

    with open('device_location.csv') as device_location_csv:
        device_location_reader = csv.reader(device_location_csv, None)
        next(device_location_reader, None)
        for row in device_location_reader:
            device_uuid = row[0]
            if device_uuid in devices:
                devices[device_uuid]['location'] = row[1]


def format_date(value):
    """
    Format a datetime.

    Args:
        value: (todo): write your description
    """
    value = int(value)
    value = datetime.datetime.fromtimestamp(value//1000)
    return f'{value:%Y-%m-%d}'


def format_timestamp(value):
    """
    Format a timestamp.

    Args:
        value: (str): write your description
    """
    value = int(value)
    value = datetime.datetime.fromtimestamp(value//1000)
    return f'{value:%Y-%m-%d %H:%M:%S}'


db = connect(dbname='mycroft', user='postgres', host='127.0.0.1')



db.autocommit = True

subscription_uuids = {}


def get_subscription_uuid(subs):
    """
    Get the uuid for a given subscription.

    Args:
        subs: (str): write your description
    """
    if subs in subscription_uuids:
        return subscription_uuids[subs]
    else:
        cursor = db.cursor()
        cursor.execute(f'select id from account.membership s where s.rate_period = \'{subs}\'')
        result = cursor.fetchone()
        subscription_uuids[subs] = result
        return result


tts_uuids = {}


def get_tts_uuid(tts):
    """
    Return a list of the given tts

    Args:
        tts: (str): write your description
    """
    if tts in tts_uuids:
        return tts_uuids[tts]
    else:
        cursor = db.cursor()
        cursor.execute(f'select id from device.text_to_speech s where s.setting_name = \'{tts}\'')
        result = cursor.fetchone()
        tts_uuids[tts] = result
        return result


def fill_account_table():
    """
    Fills the account table.

    Args:
    """
    query = 'insert into account.account(' \
            'id, ' \
            'email_address, ' \
            'password) ' \
            'values (%s, %s, %s)'
    with db.cursor() as cur:
        accounts = ((uuid, account['email'], account['password']) for uuid, account in users.items())
        execute_batch(cur, query, accounts, page_size=1000)


def fill_account_agreement_table():
    """
    Fill the account agreement agreement.

    Args:
    """
    query = 'insert into account.account_agreement(account_id, agreement_id, accept_date)' \
            'values (%s, (select id from account.agreement where agreement = %s), %s)'
    with db.cursor() as cur:
        terms = ((uuid, 'Terms of Use', format_timestamp(account['terms'])) for uuid, account in users.items() if account['terms'] != '')
        privacy = ((uuid, 'Privacy Policy', format_timestamp(account['privacy'])) for uuid, account in users.items() if account['privacy'] != '')
        execute_batch(cur, query, terms, page_size=1000)
        execute_batch(cur, query, privacy, page_size=1000)


def fill_default_wake_word():
    """
    Fill the default word.

    Args:
    """
    query1 = 'insert into device.wake_word (' \
             'id,' \
             'setting_name,' \
             'display_name,' \
             'engine)' \
             'values (%s, %s, %s, %s)'
    query2 = 'insert into device.wake_word_settings(' \
             'wake_word_id,' \
             'sample_rate,' \
             'channels,' \
             'pronunciation,' \
             'threshold,' \
             'threshold_multiplier,' \
             'dynamic_energy_ratio)' \
             'values (%s, %s, %s, %s, %s, %s, %s)'
    wake_words = [
        (hey_mycroft, 'Hey Mycroft', 'Hey Mycroft', 'precise'),
        (christopher, 'Christopher', 'Christopher', 'precise'),
        (ezra, 'Hey Ezra', 'Hey Ezra', 'precise'),
        (jarvis, 'Hey Jarvis', 'Hey Jarvis', 'precise')
    ]
    wake_word_settings = [
        (hey_mycroft, '16000', '1', 'HH EY . M AY K R AO F T', '1e-90', '1', '1.5'),
        (christopher, '16000', '1', 'K R IH S T AH F ER .', '1e-25', '1', '1.5'),
        (ezra, '16000', '1', 'HH EY . EH Z R AH', '1e-10', '1', '2.5'),
        (jarvis, '16000', '1', 'HH EY . JH AA R V AH S', '1e-25', '1', '1.5')
    ]
    with db.cursor() as cur:
        execute_batch(cur, query1, wake_words)
        execute_batch(cur, query2, wake_word_settings)


def fill_wake_word_table():
    """
    Fills a word table.

    Args:
    """
    query = 'insert into device.wake_word (' \
            'id,' \
            'setting_name,' \
            'display_name,' \
            'engine,' \
            'account_id)' \
            'values (%s, %s, %s, %s, %s)'

    def map_wake_word(user_id):
        """
        Returns the username to the user id

        Args:
            user_id: (str): write your description
        """
        wake_word_id = str(uuid.uuid4())
        wake_word = user_settings[user_id]['wake_word'].lower() if user_id in user_settings else 'hey mycroft'
        mycroft_wake_word = default_wake_words.get(wake_word)
        if mycroft_wake_word is not None:
            wake_word_id = mycroft_wake_word
        users[user_id]['wake_word_id'] = wake_word_id
        return wake_word_id, wake_word, wake_word, 'precise', user_id

    with db.cursor() as cur:
        wake_words = (map_wake_word(account_id) for account_id in users)
        wake_words = (wk for wk in wake_words if wk[0] not in (hey_mycroft, christopher, ezra, jarvis))
        execute_batch(cur, query, wake_words, page_size=1000)


def fill_account_preferences_table():
    """
    Fill user preferences.

    Args:
    """
    query = 'insert into device.account_preferences(' \
            'account_id, ' \
            'date_format, ' \
            'time_format, ' \
            'measurement_system)' \
            'values (%s, %s, %s, %s)'

    def map_account_preferences(user_uuid):
        """
        Map user_preferences.

        Args:
            user_uuid: (str): write your description
        """
        if user_uuid in user_settings:
            user_setting = user_settings[user_uuid]
            date_format = user_setting['date_format']
            if date_format == 'DMY':
                date_format = 'DD/MM/YYYY'
            else:
                date_format = 'MM/DD/YYYY'
            time_format = user_setting['time_format']
            if time_format == 'full':
                time_format = '24 Hour'
            else:
                time_format = '12 Hour'
            measurement_system = user_setting['measurement_system']
            if measurement_system == 'metric':
                measurement_system = 'Metric'
            elif measurement_system == 'imperial':
                measurement_system = 'Imperial'
            tts_type = user_setting['tts_type']
            tts_voice = user_setting['tts_voice']
            if tts_type == 'MimicSetting':
                if tts_voice == 'ap':
                    tts = 'ap'
                elif tts_voice == 'trinity':
                    tts = 'amy'
                else:
                    tts = 'ap'
            elif tts_type == 'Mimic2Setting':
                tts = 'kusal'
            elif tts_type == 'GoogleTTSSetting':
                tts = 'google'
            else:
                tts = 'ap'
            text_to_speech_id = get_tts_uuid(tts)
            users[user_uuid]['text_to_speech_id'] = text_to_speech_id
            return user_uuid, date_format, time_format, measurement_system
        else:
            text_to_speech_id = get_tts_uuid('ap')
            users[user_uuid]['text_to_speech_id'] = text_to_speech_id
            return user_uuid, 'MM/DD/YYYY', '12 Hour', 'Imperial'

    with db.cursor() as cur:
        account_preferences = (map_account_preferences(user_uuid) for user_uuid in users)
        execute_batch(cur, query, account_preferences, page_size=1000)


def fill_subscription_table():
    """
    Fills a new subscriptions for the given subscription.

    Args:
    """
    query = 'insert into account.account_membership(' \
            'account_id, ' \
            'membership_id, ' \
            'membership_ts_range, ' \
            'payment_account_id,' \
            'payment_method,' \
            'payment_id) ' \
            'values (%s, %s, %s, %s, %s, %s)'

    def map_subscription(user_uuid):
        """
        Map a subscription to a subscription.

        Args:
            user_uuid: (str): write your description
        """
        subscr = subscription[user_uuid]
        stripe_customer_id = subscr['stripe_customer_id']
        start = format_timestamp(subscr['last_payment_ts'])
        subscription_ts_range = '[{},)'.format(start)
        subscription_type = subscr['type']
        if subscription_type == 'MonthlyAccount':
            subscription_type = 'month'
        elif subscription_type == 'YearlyAccount':
            subscription_type = 'year'
        subscription_uuid = get_subscription_uuid(subscription_type)
        return user_uuid, subscription_uuid, subscription_ts_range, stripe_customer_id, 'Stripe', 'subscription_id'
    with db.cursor() as cur:
        account_subscriptions = (map_subscription(user_uuid) for user_uuid in subscription)
        execute_batch(cur, query, account_subscriptions, page_size=1000)


def fill_wake_word_settings_table():
    """
    Fills the most recent word settings table.

    Args:
    """
    query = 'insert into device.wake_word_settings(' \
            'wake_word_id,' \
            'sample_rate,' \
            'channels,' \
            'pronunciation,' \
            'threshold,' \
            'threshold_multiplier,' \
            'dynamic_energy_ratio)' \
            'values (%s, %s, %s, %s, %s, %s, %s)'

    def map_wake_word_settings(user_uuid):
        """
        Returns the word settings for the user.

        Args:
            user_uuid: (str): write your description
        """
        user_setting = user_settings[user_uuid]
        wake_word_id = users[user_uuid]['wake_word_id']
        sample_rate = user_setting['sample_rate']
        channels = user_setting['channels']
        pronunciation = user_setting['pronunciation']
        threshold = user_setting['threshold']
        threshold_multiplier = user_setting['threshold_multiplier']
        dynamic_energy_ratio = user_setting['dynamic_energy_ratio']
        return wake_word_id, sample_rate, channels, pronunciation, threshold, threshold_multiplier, dynamic_energy_ratio
    with db.cursor() as cur:
        account_wake_word_settings = (map_wake_word_settings(user_uuid) for user_uuid in users if user_uuid in user_settings)
        account_wake_word_settings = (wks for wks in account_wake_word_settings if wks[0] not in (hey_mycroft, christopher, ezra, jarvis))
        execute_batch(cur, query, account_wake_word_settings, page_size=1000)


def change_device_name():
    """
    Change user name.

    Args:
    """
    for user in user_devices:
        if user in users:
            device_names = defaultdict(list)
            for device_uuid, name in user_devices[user]:
                device_names[name].append(device_uuid)
            for name in device_names:
                uuids = device_names[name]
                if len(uuids) > 1:
                    count = 1
                    for uuid in uuids:
                        devices[uuid]['name'] = '{name}-{uuid}'.format(name=name, uuid=uuid)
                        count += 1


def fill_device_table():
    """
    Fetch the device table.

    Args:
    """
    query = 'insert into device.device(' \
            'id, ' \
            'account_id, ' \
            'name, ' \
            'placement,' \
            'platform,' \
            'enclosure_version,' \
            'core_version,' \
            'wake_word_id,' \
            'geography_id,' \
            'text_to_speech_id) ' \
            'values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
    query2 = 'insert into device.geography(' \
             'id,' \
             'account_id,' \
             'country_id,' \
             'region_id,' \
             'city_id,' \
             'timezone_id) ' \
             'values (%s, %s, %s, %s, %s, %s)'

    with db.cursor() as cur:
        query_geography = """
        SELECT
            city.id, region.id, country.id, timezone.id
        FROM 
            geography.city city
        INNER JOIN
            geography.region region ON city.region_id = region.id
        INNER JOIN
            geography.country country ON region.country_id = country.id
        INNER JOIN
            geography.timezone timezone ON country.id = timezone.country_id
        WHERE
            city.name = %s and region.name = %s and timezone.name = %s;
        """
        cur.execute(query_geography, ('Lawrence', 'Kansas', 'America/Chicago'))
        city_default, region_default, country_default, timezone_default = cur.fetchone()

    def map_geography(account_id, device_id):
        """
        Map the geography to geography

        Args:
            account_id: (str): write your description
            device_id: (int): write your description
        """
        geography_id = str(uuid.uuid4())
        with db.cursor() as cur:
            query = """
            SELECT
                city.id, region.id, country.id, timezone.id
            FROM 
                geography.city city
            INNER JOIN
                geography.region region ON city.region_id = region.id
            INNER JOIN
                geography.country country ON region.country_id = country.id
            INNER JOIN
                geography.timezone timezone ON country.id = timezone.country_id
            WHERE
                city.name = %s and region.name = %s and timezone.name = %s and country.name = %s;
            """
            location_uuid = devices[device_id].get('location')
            if location_uuid is not None:
                location = locations[location_uuid]
                timezone_entity = timezones[location['timezone']]
                timezone = timezone_entity['code']
                city_entity = cities[location['city']]
                city = city_entity['name']
                region_entity = regions[city_entity['region']]
                region = region_entity['name']
                country_entity = countries[region_entity['country']]
                country = country_entity['name']
                cur.execute(query, (city, region, timezone, country))
                result = cur.fetchone()
                if result is not None:
                    city, region, country, timezone = result
                    return geography_id, account_id, country, region, city, timezone
        return geography_id, account_id, country_default, region_default, city_default, timezone_default

    def map_device(device_id):
        """
        Map a device.

        Args:
            device_id: (int): write your description
        """
        device = devices[device_id]
        account_id = device['user_uuid']
        name = device['name']
        placement = device['description']
        platform = device['platform']
        enclosure_version = device['enclosure_version']
        core_version = device['core_version']
        wake_word_id = users[account_id]['wake_word_id']
        geography_id = device['geography_id']

        user_setting = user_settings[account_id]
        tts_type = user_setting['tts_type']
        tts_voice = user_setting['tts_voice']
        if tts_type == 'MimicSetting':
            if tts_voice == 'ap':
                tts = 'ap'
            elif tts_voice == 'trinity':
                tts = 'amy'
            else:
                tts = 'ap'
        elif tts_type == 'Mimic2Setting':
            tts = 'kusal'
        elif tts_type == 'GoogleTTSSetting':
            tts = 'google'
        else:
            tts = 'ap'
        text_to_speech_id = get_tts_uuid(tts)

        return device_id, account_id, name, placement, platform, enclosure_version, core_version, wake_word_id, geography_id, text_to_speech_id
    with db.cursor() as cur:
        geography_batch = []
        for user in user_devices:
            if user in users and user in user_settings:
                aux = user_devices[user]
                device_id, _ = aux[0]
                geography = map_geography(user, device_id)
                geography_batch.append(geography)
                for device_id, name in aux:
                    devices[device_id]['geography_id'] = geography[0]
        execute_batch(cur, query2, geography_batch, page_size=1000)
        devices_batch = (map_device(device_id) for user in user_devices if user in users and user in user_settings for device_id, name in user_devices[user])
        execute_batch(cur, query, devices_batch, page_size=1000)


def fill_skills_table():
    """
    Fill out the skill table with skill table.

    Args:
    """
    skills_batch = []
    settings_display_batch = []
    device_skill_batch = []
    for user in user_devices:
        if user in users and user in user_settings:
            for device_uuid, name in user_devices[user]:
                if device_uuid in device_to_skill:
                    for skill_uuid in device_to_skill[device_uuid]:
                        skill = skills[skill_uuid]
                        skill_name = skill['name']
                        identifier = skill['identifier']
                        sections = []
                        settings = {}
                        if skill_uuid in skill_to_section:
                            for section_uuid in skill_to_section[skill_uuid]:
                                section = skill_sections[section_uuid]
                                section_name = section['section']
                                fields = []
                                if section_uuid in section_to_field:
                                    for field_uuid in section_to_field[section_uuid]:
                                        fields.append(skill_fields[field_uuid])
                                        if field_uuid in skill_field_values:
                                            settings[skill_fields[field_uuid]['name']] = skill_field_values[field_uuid]['field_value']
                                sections.append({'name': section_name, 'fields': fields})
                        skill_setting_display = {
                            'name': skill_name,
                            'identifier': identifier,
                            'skillMetadata': {'sections': sections}
                        }
                        skills_batch.append((skill_uuid, skill_name))
                        meta_id = str(uuid.uuid4())
                        settings_display_batch.append((meta_id, skill_uuid, json.dumps(skill_setting_display)))
                        device_skill_batch.append((device_uuid, skill_uuid, meta_id, json.dumps(settings)))

    with db.cursor() as curr:
        query = 'insert into skill.skill(id, name) values (%s, %s)'
        execute_batch(curr, query, skills_batch, page_size=1000)
        query = 'insert into skill.settings_display(id, skill_id, settings_display) values (%s, %s, %s)'
        execute_batch(curr, query, settings_display_batch, page_size=1000)
        query = 'insert into device.device_skill(device_id, skill_id, skill_settings_display_id, settings) ' \
                'values (%s, %s, %s, %s)'
        execute_batch(curr, query, device_skill_batch, page_size=1000)


def analyze_locations():
    """
    Analyze country and region.

    Args:
    """
    matches = 0
    mismatches = 0
    g_mismatches = defaultdict(lambda: defaultdict(list))
    for city in cities.values():
        region = regions[city['region']]
        country = countries[region['country']]
        city_name = city['name']
        region_name = region['name']
        country_name = country['name']
        remove = ['District', 'Region', 'Development', 'Prefecture', 'Community', 'County', 'Province', 'Division', 'Voivodeship', 'State', 'of', 'Governorate']
        with db.cursor() as curr:
            original_region_name = region_name
            region_name = ' '.join(i for i in region_name.split() if i not in remove)
            query = 'select city.name ' \
                    'from geography.city city ' \
                    'inner join geography.region region on city.region_id = region.id ' \
                    'inner join geography.country country on region.country_id = country.id ' \
                    'where ' \
                    'city.name = \'{}\' and ' \
                    '(region.name = \'{}\' or region.name = \'{}\') and ' \
                    'country.name = \'{}\''\
                    .format(
                        city_name.replace('\'', '\'\''),
                        original_region_name.replace('\'', '\'\''),
                        region_name.replace('\'', '\'\''),
                        country_name.replace('\'', '\'\'')
                    )
            curr.execute(query)
            result = curr.fetchone()
            if result is None:
                mismatches += 1
                g_mismatches[country_name][region_name].append(city_name)
            else:
                matches += 1

    for country2, regions2 in g_mismatches.items():
        for region2, cities2 in regions2.items():
            for city2 in cities2:
                print('{} - {} - {}'.format(country2, region2, city2))

    print('Number os mismatches: {}'.format(mismatches))


def analyze_location_2():
    """
    Analyze location coordinates.

    Args:
    """
    aux = defaultdict(lambda: defaultdict(lambda: defaultdict(str)))

    locations_from_db = defaultdict(list)
    with db.cursor() as cur:
        cur.execute('select '
                    'c1.id, '
                    'c1.name, '
                    'c1.latitude, '
                    'c1.longitude, '
                    'r.name, '
                    'c2.name, '
                    'c2.iso_code '
                    'from geography.city c1 '
                    'inner join geography.region r on c1.region_id = r.id '
                    'inner join geography.country c2 on r.country_id = c2.id')
        for c1_id, c1, latitude, longitude, r, c2_name, c2_code in cur:
            aux[c2_name][r][c1] = c1_id
            locations_from_db[c2_code].append((c1, latitude, longitude))

    for location_uuid, location in locations.items():
        coordinate = coordinates[location_uuid]
        city = cities[location['city']]
        city_name = city['name']
        region = regions[city['region']]
        region_name = region['name']
        country = countries[region['country']]
        country_code = country['code']
        country_name = country['name']

        res = aux.get(country_name)
        if res is not None:
            res = res.get(region_name)
            if res is not None:
                res = res.get(city_name)
                if res is not None:
                    print('Match: {}'.format(city_name))
                    continue
        min_dist = None
        result_name = None
        for c1_name, latitude, longitude in locations_from_db[country_code]:
            point1 = (float(latitude), float(longitude))
            point2 = (float(coordinate['latitude']), float(coordinate['longitude']))
            dist = distance(point1, point2).km
            if min_dist is None or dist < min_dist:
                min_dist = dist
                result_name = c1_name
        print('Actual: {}, calculated: {}'.format(city_name, result_name))


start = time.time()
load_csv()
end = time.time()

print('Time to load CSVs {}'.format(end - start))

start = time.time()
print('Importing account table')
#fill_account_table()
print('Importing agreements table')
#fill_account_agreement_table()
print('Importing account preferences table')
#fill_account_preferences_table()
print('Importing subscription table')
#fill_subscription_table()
print('Importing wake word table')
#fill_default_wake_word()
#fill_wake_word_table()
print('Importing wake word settings table')
#fill_wake_word_settings_table()
print('Importing device table')
#change_device_name()
#fill_device_table()
print('Importing skills table')
#fill_skills_table()
analyze_location_2()
end = time.time()
print('Time to import: {}'.format(end-start))
