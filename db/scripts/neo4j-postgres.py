import csv
import datetime

from psycopg2 import connect
import uuid

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
            skill_fields[field_uuid]['section_uuid'] = section_uuid
            skill_fields[field_uuid]['name'] = row[2]
            skill_fields[field_uuid]['type'] = row[3]
            skill_fields[field_uuid]['label'] = row[4]
            skill_fields[field_uuid]['hint'] = row[5]
            skill_fields[field_uuid]['placeholder'] = row[6]
            skill_fields[field_uuid]['hide'] = row[7]
            skill_fields[field_uuid]['options'] = row[8]
            skill_fields[field_uuid]['order'] = row[9]
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


def parse_user_setting(user_uuid) -> (str, str, str, str):
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
        wake_word = user_setting['wake_word']
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
        sample_rate = user_setting['sample_rate']
        channels = user_setting['channels']
        pronunciation = user_setting['pronunciation']
        threshold = user_setting['threshold']
        threshold_multiplier = user_setting['threshold_multiplier']
        dynamic_energy_ratio = user_setting['dynamic_energy_ratio']
        return date_format, time_format, measurement_system, tts, wake_word, sample_rate, channels, pronunciation, threshold, threshold_multiplier, dynamic_energy_ratio
    else:
        return 'MM/DD/YYYY', '12 Hour', 'Imperial', 'ap', 'Hey Mycroft', '16000', '1', 'HH EY . M AY K R AO F T', '1e-90', '1.0', '1.5'


def format_date(value):
    value = int(value)
    value = datetime.datetime.fromtimestamp(value//1000)
    return f'{value:%Y-%m-%d}'


def format_timestamp(value):
    value = int(value)
    value = datetime.datetime.fromtimestamp(value//1000)
    return f'{value:%Y-%m-%d %H:%M:%S}'


def parse_subscription(user_uuid):
    if user_uuid in subscription:
        subscr = subscription[user_uuid]
        stripe_customer_id = subscr['stripe_customer_id']
        start = format_timestamp(subscr['last_payment_ts'])
        subscription_ts_range = '[{},)'.format(start)
        subscription_type = subscr['type']
        if subscription_type == 'MonthlyAccount':
            subscription_type = 'month'
        elif subscription_type == 'YearlyAccount':
            subscription_type = 'year'
        return subscription_ts_range, stripe_customer_id, subscription_type
    else:
        return '', '', ''


db = connect(dbname='mycroft', user='postgres', host='127.0.0.1')
db.autocommit = True

subscription_uuids = {}


def get_subscription_uuid(subs):
    if subs in subscription_uuids:
        return subscription_uuids[subs]
    else:
        cursor = db.cursor()
        cursor.execute(f'select id from account.subscription s where s.rate_period = \'{subs}\'')
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


def create_account(user_uuid):
    user = users[user_uuid]
    email = user['email']
    password = user['password']
    date_format, time_format, measurement_system, tts, wake_word, sample_rate, channels, pronunciation, threshold, threshold_multiplier, dynamic_energy_ratio = parse_user_setting(user_uuid)
    subscription_ts_range, stripe_customer_id, subscription_type = parse_subscription(user_uuid)
    cursor = db.cursor()

    query = 'insert into account.account(' \
            'id, ' \
            'email_address, ' \
            'password) ' \
            'values (%s, %s, %s)'
    params = (user_uuid, email, password)
    cursor.execute(query, params)

    wake_word_id = str(uuid.uuid4())
    user['wake_word_id'] = wake_word_id
    query = 'insert into device.wake_word (' \
            'id,' \
            'wake_word,' \
            'account_id)' \
            'values (%s, %s, %s)'
    params = (wake_word_id, wake_word, user_uuid)
    cursor.execute(query, params)

    text_to_speech_id = get_tts_uuid(tts)
    user['text_to_speech_id'] = text_to_speech_id

    query = 'insert into device.account_preferences(' \
            'account_id, ' \
            'date_format, ' \
            'time_format, ' \
            'measurement_system,' \
            'wake_word_id,' \
            'text_to_speech_id)' \
            'values (%s, %s, %s, %s, %s, %s)'
    params = (user_uuid, date_format, time_format, measurement_system, wake_word_id, text_to_speech_id)
    cursor.execute(query, params)

    if subscription_ts_range != '':
        subscription_uuid = get_subscription_uuid(subscription_type)
        query = 'insert into account.account_subscription(' \
                'account_id, ' \
                'subscription_id, ' \
                'subscription_ts_range, ' \
                'stripe_customer_id) ' \
                'values (%s, %s, %s, %s)'
        params = (user_uuid, subscription_uuid, subscription_ts_range, stripe_customer_id)
        cursor.execute(query, params)

    query = 'insert into device.wake_word_settings(' \
            'wake_word_id,' \
            'sample_rate,' \
            'channels,' \
            'pronunciation,' \
            'threshold,' \
            'threshold_multiplier,' \
            'dynamic_energy_ratio)' \
            'values (%s, %s, %s, %s, %s, %s, %s)'
    params = (wake_word_id, sample_rate, channels, pronunciation, threshold, threshold_multiplier, dynamic_energy_ratio)
    cursor.execute(query, params)

load_csv()

for account in users:
    print('Creating user {}'.format(account))
    create_account(account)


def create_device(device_uuid, category):
    print('Creating device {} with category {}'.format(device_uuid, category))
    device = devices[device_uuid]
    account_id = device['user_uuid']
    device_name = device['name']
    description = device['description']
    platform = device['platform']
    enclosure_version = device['enclosure_version']
    core_version = device['core_version']

    wake_word_id = users[account_id]['wake_word_id']
    text_to_speech_id = users[account_id]['text_to_speech_id']

    cursor = db.cursor()
    query = 'select cat.id from device.category cat left join account.account acc on cat.account_id = acc.id where acc.id = %s and cat.category = %s'
    params = (account_id, category)
    cursor.execute(query, params)
    category_id = cursor.fetchone()
    if category_id is None:
        query = 'insert into device.category(id, account_id, category) values (%s, %s, %s)'
        category_id = str(uuid.uuid4())
        params = (category_id, account_id, category)
        cursor.execute(query, params)

    query = 'insert into device.device(' \
            'id, ' \
            'account_id, ' \
            'name, ' \
            'category_id,' \
            'placement,' \
            'platform,' \
            'enclosure_version,' \
            'core_version,' \
            'wake_word_id,' \
            'text_to_speech_id) ' \
            'values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
    params = (device_uuid, account_id, device_name, category_id, description, platform, enclosure_version, core_version, wake_word_id, text_to_speech_id)
    cursor.execute(query, params)


def create_device_skills(device_uuid):
    cursor = db.cursor()
    if device_uuid in device_to_skill:
        for skill_uuid in device_to_skill[device_uuid]:
            skill = skills[skill_uuid]
            version_hash = skill['identifier']
            skill_name = skill['name']
            print('Creating skill with id {}'.format(skill_uuid))
            query = 'insert into skill.skill(id, name) values (%s, %s)'
            params = (skill_uuid, skill_name)
            cursor.execute(query, params)

            skill_version_id = str(uuid.uuid4())
            query = 'insert into skill.setting_version(id, skill_id, version_hash) values (%s, %s, %s)'
            params = (skill_version_id, skill_uuid, version_hash)
            cursor.execute(query, params)

            device_skill_id = str(uuid.uuid4())
            query = 'insert into device.device_skill (id, device_id, skill_id) values (%s, %s, %s)'
            params = (device_skill_id, device_uuid, skill_uuid)
            cursor.execute(query, params)
            for section_uuid in skill_to_section[skill_uuid]:
                print('Creating section with id {}'.format(section_uuid))
                query = 'insert into skill.setting_section(id, skill_version_id, section, display_order) values (%s, %s, %s, %s)'
                section = skill_sections[section_uuid]
                section_name = section['section']
                display_order = section['display_order']
                params = (section_uuid, skill_version_id, section_name, display_order)
                cursor.execute(query, params)
                for field_uuid in section_to_field[section_uuid]:
                    print('Creating field with id {}'.format(field_uuid))
                    query = 'insert into skill.setting(id, setting_section_id, setting, setting_type, hint, label, placeholder, hidden, options, display_order) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
                    field = skill_fields[field_uuid]
                    setting = field['name']
                    setting_type = field['type']
                    hint = field['hint']
                    label = field['label']
                    placeholder = field['placeholder']
                    hidden = field['hide']
                    options = field['options']
                    display_order = field['order']
                    params = (field_uuid, section_uuid, setting, setting_type, hint, label, placeholder, hidden == 'true', options, display_order)
                    cursor.execute(query, params)

                    field_value = skill_field_values[field_uuid]['field_value']
                    query = 'insert into device.skill_setting(device_skill_id, setting_id, value) values (%s, %s, %s)'
                    params = (device_skill_id, field_uuid, field_value)
                    cursor.execute(query, params)


def create_devices():
    for user in user_devices:
        if user in users:
            category = {}
            for device_uuid, name in user_devices[user]:
                if name in category:
                    category[name].append(device_uuid)
                else:
                    category[name] = [device_uuid]
            print('User {} Categories: {}'.format(user, category))
            for name in category:
                group = 1
                for device_uuid in category[name]:
                    create_device(device_uuid, 'Group {}'.format(group))
                    create_device_skills(device_uuid)
                    group += 1


create_devices()

