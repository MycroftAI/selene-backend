-- This set of schema changes is for the wake word collection project.
--
-- First, Create the wake word schema and the tables it will contain.  The device.wake_word
-- and device.wake_word_settings tables are being moved to this schema.  A new table to
-- track Precise models is also included.
--
-- The new wake word table is now a domain table of all possible wake words.  The account ID
-- is moved from the wake_word level to the pocketsphinx settings level to accommodate this.
CREATE SCHEMA wake_word;
CREATE TABLE wake_word.wake_word (
    id              uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    name            text        NOT NULL,
    engine          text        NOT NULL,
    insert_ts       TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (name, engine)
);
CREATE TABLE wake_word.pocketsphinx_settings (
    id                      uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    wake_word_id            uuid        NOT NULL REFERENCES wake_word.wake_word ON DELETE CASCADE,
    account_id              uuid        REFERENCES account.account ON DELETE CASCADE,
    sample_rate             INTEGER,
    channels                INTEGER,
    pronunciation           text,
    threshold               text,
    threshold_multiplier    NUMERIC,
    dynamic_energy_ratio    NUMERIC,
    insert_ts               TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (wake_word_id, account_id)
);
GRANT USAGE ON SCHEMA wake_word TO selene;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA wake_word TO selene;

-- Populate the new wake_word.wake_word table from the existing version.
-- Some wake words on the existing table are preceded by a space.  The TRIM
-- function will remove that space before adding it to the new table.
INSERT INTO
    wake_word.wake_word (name, engine)
VALUES
    ('hey mycroft', 'precise')
;
INSERT INTO
    wake_word.wake_word (name, engine)
    (
        SELECT
            DISTINCT TRIM(LEADING FROM setting_name),
            'pocketsphinx'
        FROM
            device.wake_word
    )
;

-- Populate the new wake_word.pocketsphinx_settings table from the device.wake_word_settings
-- table.  Account ID is populated from the wake_word.wake_word table because it is
-- now a domain table.
INSERT INTO
    wake_word.pocketsphinx_settings (
        wake_word_id,
        account_id,
        sample_rate,
        channels,
        pronunciation,
        threshold,
        threshold_multiplier,
        dynamic_energy_ratio)
    (
        SELECT
            ww.id,
            dww.account_id,
            wws.sample_rate,
            wws.channels,
            wws.pronunciation,
            wws.threshold,
            wws.threshold_multiplier,
            wws.dynamic_energy_ratio
        FROM
            device.wake_word dww
            INNER JOIN device.wake_word_settings wws ON dww.id = wws.wake_word_id
            INNER JOIN wake_word.wake_word as ww ON TRIM(LEADING FROM dww.setting_name) = ww.name
    )
;

-- Update the device.device table to reference the new wake word IDs.
--      * Drop the existing constraint
--      * Update the IDs
--      * Add new constraint to wake_word.wake_word table.
ALTER TABLE device.device DROP CONSTRAINT device_wake_word_id_fkey;
UPDATE
    device.device
SET
    wake_word_id = subquery.wake_word_id
FROM
    (
        SELECT
            d.id as device_id,
            ww.id as wake_word_id
        FROM
            device.device d
            INNER JOIN device.wake_word as dww ON d.wake_word_id = dww.id
            INNER JOIN wake_word.wake_word as ww ON TRIM(LEADING FROM dww.setting_name) = ww.name
    ) AS subquery
WHERE
    device.device.id = subquery.device_id
;
ALTER TABLE device.device ADD CONSTRAINT device_wake_word_id_fkey
    FOREIGN KEY (wake_word_id) REFERENCES wake_word.wake_word (id);

-- Update the device.device table to reference the new wake word IDs.
--      * Drop the existing constraint
--      * Update the IDs
--      * Add new constraint to wake_word.wake_word table.ALTER TABLE device.device DROP CONSTRAINT device_wake_word_id_fkey;
ALTER TABLE device.account_defaults DROP CONSTRAINT account_defaults_wake_word_id_fkey;
UPDATE
    device.account_defaults
SET
    wake_word_id = subquery.wake_word_id
FROM
    (
        SELECT
            ad.id as account_default_id,
            ww.id as wake_word_id
        FROM
            device.account_defaults ad
            INNER JOIN device.wake_word as dww ON ad.wake_word_id = dww.id
            INNER JOIN wake_word.wake_word as ww ON TRIM(LEADING FROM dww.setting_name) = ww.name
    ) AS subquery
WHERE
    device.account_defaults.id = subquery.account_default_id
;
ALTER TABLE device.account_defaults ADD CONSTRAINT account_defaults_wake_word_id_fkey
    FOREIGN KEY (wake_word_id) REFERENCES wake_word.wake_word (id);

-- With all the wake word data moved to the new schema, drop the existing tables.
DROP TABLE device.wake_word_settings;
DROP TABLE device.wake_word;

-- Create the tagging schema
CREATE SCHEMA tagging;
CREATE TYPE tagging_file_origin_enum AS ENUM ('mycroft', 'selene', 'manual');
CREATE TYPE tagging_file_status_enum AS ENUM (
    'uploaded',
    'stored',
    'pending delete',
    'deleted'
);
CREATE TABLE tagging.file_location (
    id              uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    server          inet        NOT NULL,
    directory       text        NOT NULL,
    insert_ts       TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (server, directory)
);
CREATE TABLE tagging.wake_word_file (
    id                  uuid                        PRIMARY KEY DEFAULT gen_random_uuid(),
    name                text                        NOT NULL UNIQUE,
    wake_word_id        uuid                        NOT NULL REFERENCES wake_word.wake_word,
    origin              tagging_file_origin_enum    NOT NULL,
    submission_date     date                        NOT NULL DEFAULT CURRENT_DATE,
    file_location_id    uuid                        NOT NULL REFERENCES tagging.file_location,
    account_id          uuid,
    status              tagging_file_status_enum    NOT NULL DEFAULT 'uploaded'::tagging_file_status_enum,
    insert_ts           TIMESTAMP                   NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE tagging.tagger (
    id              uuid                PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type     tagger_type_enum    NOT NULL,
    entity_id       text                NOT NULL,
    insert_ts       TIMESTAMP           NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (entity_type, entity_id)
);
CREATE TABLE tagging.session (
    id                  uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    tagger_id           text        NOT NULL,
    session_ts_range    tsrange     NOT NULL DEFAULT '[now,]'::tsrange,
    note                text,
    insert_ts           timestamp   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    EXCLUDE USING gist (tagger_id WITH =, session_ts_range with &&),
    UNIQUE (tagger_id, session_ts_range)
);
CREATE TABLE tagging.tag (
    id              uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    name            text        NOT NULL UNIQUE,
    title           text        NOT NULL,
    instructions    text        NOT NULL,
    insert_ts       TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE tagging.tag_value (
    id              uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    tag_id          uuid        NOT NULL REFERENCES tagging.tag,
    value           text        NOT NULL,
    display         text        NOT NULL,
    insert_ts       TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (tag_id, value)
);
CREATE TABLE tagging.wake_word_file_tag (
    id              uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    wake_word_file_id   uuid    NOT NULL REFERENCES tagging.wake_word_file,
    session_id      uuid        NOT NULL REFERENCES tagging.session,
    tag_id          uuid        NOT NULL REFERENCES tagging.tag,
    tag_value_id    uuid        NOT NULL REFERENCES tagging.tag_value,
    insert_ts       TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (wake_word_file_id, session_id, tag_id)
);
CREATE TABLE tagging.wake_word_file_designation (
    id                  uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    wake_word_file_id   uuid        NOT NULL REFERENCES tagging.wake_word_file,
    tag_id              uuid        NOT NULL REFERENCES tagging.tag,
    tag_value_id        uuid        NOT NULL REFERENCES tagging.tag_value,
    insert_ts           TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (wake_word_file_id, tag_id)
);

-- Give the selene user access to the schema and its tables
GRANT USAGE ON SCHEMA tagging TO selene;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA tagging TO selene;

--  Populate the static data in tagging.tag and tagging.tag_values
INSERT INTO
    tagging.tag (name, title, instructions)
VALUES
    (
        'wake word',
        'Do you hear the wake word',
        'Indicate if you did not hear the wake word (no); heard a partial wake word or something '
         || 'that sounds similar to the wake word (no, but similar); heard multiple occurrences of '
         || 'the wake word (yes, multiple); or heard a single occurrence of the full wake word (yes, '
         || 'once).  Using the "Hey Mycroft" wake word as an example, answer "no, but similar" if you '
         || 'hear something like "Mycroft", "Microsoft", "Hey Minecraft" or "Hey Mike Ross".'
    ),
    (
        'gender',
        'What is the perceived',
        'For the speaker in this audio clip choose which category best describes the pitch and timbre.'
    ),
    (
        'age',
        'What is the perceived',
        'For the speaker in this audio clip choose which category best describes the their age.'
    ),
    (
        'background noise',
        'Do you hear any',
        'Besides the voice of the speaker, can you hear any background noise (e.g. fan, appliance, '
        || 'vehicle, television or radio)?'
    )
;
INSERT INTO
    tagging.tag_value (tag_id, value, display)
VALUES
    ((SELECT id FROM tagging.tag WHERE tag.name = 'wake_word'), 'no', 'NO'),
    ((SELECT id FROM tagging.tag WHERE tag.name = 'wake_word'), 'similar', 'NO, BUT SIMILAR'),
    ((SELECT id FROM tagging.tag WHERE tag.name = 'wake_word'), 'multiple', 'YES, MULTIPLE'),
    ((SELECT id FROM tagging.tag WHERE tag.name = 'wake_word'), 'yes', 'YES, SINGLE'),
    ((SELECT id FROM tagging.tag WHERE name = 'gender'), 'male', 'MASCULINE'),
    ((SELECT id FROM tagging.tag WHERE name = 'gender'), 'neutral', 'NEUTRAL'),
    ((SELECT id FROM tagging.tag WHERE name = 'gender'), 'female', 'FEMININE'),
    ((SELECT id FROM tagging.tag WHERE name = 'age'), 'child', 'CHILD'),
    ((SELECT id FROM tagging.tag WHERE name = 'age'), 'neutral', 'NEUTRAL'),
    ((SELECT id FROM tagging.tag WHERE name = 'age'), 'adult', 'ADULT'),
    ((SELECT id FROM tagging.tag WHERE name = 'background noise'), 'no', 'NO NOISE'),
    ((SELECT id FROM tagging.tag WHERE name = 'background noise'), 'some', 'SOME NOISE'),
    ((SELECT id FROM tagging.tag WHERE name = 'background noise'), 'yes', 'ADULT')
;
