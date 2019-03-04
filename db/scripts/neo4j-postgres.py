import csv
import datetime
import json
import uuid
from collections import defaultdict

import time
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


def load_csv():
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


def format_date(value):
    value = int(value)
    value = datetime.datetime.fromtimestamp(value//1000)
    return f'{value:%Y-%m-%d}'


def format_timestamp(value):
    value = int(value)
    value = datetime.datetime.fromtimestamp(value//1000)
    return f'{value:%Y-%m-%d %H:%M:%S}'



db = connect(dbname='mycroft', user='postgres', host='127.0.0.1')
db.autocommit = True

subscription_uuids = {}


def get_subscription_uuid(subs):
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
    if tts in tts_uuids:
        return tts_uuids[tts]
    else:
        cursor = db.cursor()
        cursor.execute(f'select id from device.text_to_speech s where s.setting_name = \'{tts}\'')
        result = cursor.fetchone()
        tts_uuids[tts] = result
        return result


def fill_account_table():
    query = 'insert into account.account(' \
            'id, ' \
            'email_address, ' \
            'password) ' \
            'values (%s, %s, %s)'
    with db.cursor() as cur:
        accounts = ((uuid, account['email'], account['password']) for uuid, account in users.items())
        execute_batch(cur, query, accounts, page_size=1000)


def fill_account_agreement_table():
    query = 'insert into account.agreement(account_id, agreement_id, accept_date)' \
            'values (%s, select id from account.agreement where agreement = %s, %s)'
    with db.cursor() as cur:
        terms = [(uuid, format_timestamp(account['terms'])) for uuid, account in users.items()]
        privacy = [(uuid, format_timestamp(account['privacy'])) for uuid, account in users.items()]
        execute_batch(cur, query, terms+privacy, page_size=1000)


def fill_wake_word_table():
    query = 'insert into device.wake_word (' \
            'id,' \
            'wake_word,' \
            'engine,' \
            'account_id)' \
            'values (%s, %s, %s, %s)'

    def map_wake_word(user_id):
        wake_word_id = str(uuid.uuid4())
        wake_word = user_settings[user_id]['wake_word'] if user_id in user_settings else 'Hey Mycroft'
        users[user_id]['wake_word_id'] = wake_word_id
        return wake_word_id, wake_word, 'precise', user_id

    with db.cursor() as cur:
        wake_words = (map_wake_word(account_id) for account_id in users)
        execute_batch(cur, query, wake_words, page_size=1000)


def fill_account_preferences_table():
    query = 'insert into device.account_preferences(' \
            'account_id, ' \
            'date_format, ' \
            'time_format, ' \
            'measurement_system,' \
            'wake_word_id,' \
            'text_to_speech_id)' \
            'values (%s, %s, %s, %s, %s, %s)'

    def map_account_preferences(user_uuid):
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
            return user_uuid, date_format, time_format, measurement_system, users[user_uuid]['wake_word_id'], text_to_speech_id
        else:
            text_to_speech_id = get_tts_uuid('ap')
            users[user_uuid]['text_to_speech_id'] = text_to_speech_id
            return user_uuid, 'MM/DD/YYYY', '12 Hour', 'Imperial', users[user_uuid]['wake_word_id'], text_to_speech_id

    with db.cursor() as cur:
        account_preferences = (map_account_preferences(user_uuid) for user_uuid in users)
        execute_batch(cur, query, account_preferences, page_size=1000)


def fill_subscription_table():
    query = 'insert into account.account_membership(' \
            'account_id, ' \
            'membership_id, ' \
            'membership_ts_range, ' \
            'payment_account_id,' \
            'payment_method) ' \
            'values (%s, %s, %s, %s, %s)'

    def map_subscription(user_uuid):
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
        return user_uuid, subscription_uuid, subscription_ts_range, stripe_customer_id, 'Stripe'
    with db.cursor() as cur:
        account_subscriptions = (map_subscription(user_uuid) for user_uuid in subscription)
        execute_batch(cur, query, account_subscriptions, page_size=1000)


def fill_wake_word_settings_table():
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
        execute_batch(cur, query, account_wake_word_settings, page_size=1000)


def change_device_name():
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
    query = 'insert into device.device(' \
            'id, ' \
            'account_id, ' \
            'name, ' \
            'placement,' \
            'platform,' \
            'enclosure_version,' \
            'core_version,' \
            'wake_word_id,' \
            'text_to_speech_id) ' \
            'values (%s, %s, %s, %s, %s, %s, %s, %s, %s)'

    def map_device(device_id):
        device = devices[device_id]
        account_id = device['user_uuid']
        name = device['name']
        placement = device['description']
        platform = device['platform']
        enclosure_version = device['enclosure_version']
        core_version = device['core_version']
        wake_word_id = users[account_id]['wake_word_id']
        text_to_speech_id = users[account_id]['text_to_speech_id']
        return device_id, account_id, name, placement, platform, enclosure_version, core_version, wake_word_id, text_to_speech_id
    with db.cursor() as cur:
        devices_batch = (map_device(device_id) for user in user_devices if user in users for device_id, name in user_devices[user])
        execute_batch(cur, query, devices_batch, page_size=1000)


def fill_skills_table():
    skills_batch = []
    settings_meta_batch = []
    device_skill_batch = []
    for user in user_devices:
        if user in users:
            for device_uuid, name in user_devices[user]:
                if device_uuid in device_to_skill:
                    for skill_uuid in device_to_skill[device_uuid]:
                        skill = skills[skill_uuid]
                        skill_name = skill['name']
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
                                        settings[skill_fields[field_uuid]['name']] = skill_field_values[field_uuid]['field_value']
                                sections.append({'name': section_name, 'fields': fields})
                        skill_setting_meta = {'name': skill_name, 'skillMetadata': {'sections': sections}}
                        skills_batch.append((skill_uuid, skill_name))
                        meta_id = str(uuid.uuid4())
                        settings_meta_batch.append((meta_id, skill_uuid, json.dumps(skill_setting_meta)))
                        device_skill_batch.append((device_uuid, skill_uuid, meta_id, json.dumps(settings)))

    with db.cursor() as curr:
        query = 'insert into skill.skill(id, name) values (%s, %s)'
        execute_batch(curr, query, skills_batch, page_size=1000)
        query = 'insert into skill.settings_display(id, skill_id, settings_display) values (%s, %s, %s)'
        execute_batch(curr, query, settings_meta_batch, page_size=1000)
        query = 'insert into device.device_skill(device_id, skill_id, skill_settings_display_id, settings) ' \
                'values (%s, %s, %s, %s)'
        execute_batch(curr, query, device_skill_batch, page_size=1000)

start = time.time()
load_csv()
end = time.time()

print('Time to load CSVs {}'.format(end - start))

start = time.time()
print('Importing account table')
fill_account_table()
print('Importing wake word table')
fill_wake_word_table()
print('Importing account preferences table')
fill_account_preferences_table()
print('Importing subscription table')
fill_subscription_table()
print('Importing wake word settings table')
fill_wake_word_settings_table()
print('Importing device table')
change_device_name()
fill_device_table()
print('Filling skills table')
fill_skills_table()
end = time.time()
print('Time to import: {}'.format(end-start))
