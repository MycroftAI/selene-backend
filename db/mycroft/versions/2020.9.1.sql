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

-- Create the tagging schema and the first two tables to reside within it.
-- More tagging tables will be added in the next iteration.
CREATE SCHEMA tagging;
CREATE TYPE tagging_file_origin_enum AS ENUM ('mycroft', 'selene', 'manual');
CREATE TABLE tagging.file_location (
    id              uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    server          inet        NOT NULL,
    directory       text        NOT NULL,
    insert_ts       TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (server, directory)
);
CREATE TABLE tagging.file (
    id                  uuid                        PRIMARY KEY DEFAULT gen_random_uuid(),
    name                text                        NOT NULL UNIQUE,
    origin              tagging_file_origin_enum    NOT NULL,
    submission_date     date                        NOT NULL DEFAULT CURRENT_DATE,
    file_location_id    uuid                        REFERENCES tagging.file_location,
    account_id          uuid,
    insert_ts           TIMESTAMP                   NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tagging.wake_word_file (
    wake_word_id    uuid    NOT NULL REFERENCES wake_word.wake_word
)
INHERITS (tagging.file);
GRANT USAGE ON SCHEMA wake_word TO selene;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA wake_word TO selene;
