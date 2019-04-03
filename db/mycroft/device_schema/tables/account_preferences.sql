-- Account level preferences that pertain to device function.
CREATE TABLE device.account_preferences (
    id                  uuid                    PRIMARY KEY
            DEFAULT gen_random_uuid(),
    account_id          uuid                    NOT NULL
            UNIQUE
            REFERENCES account.account ON DELETE CASCADE,
    date_format         date_format_enum        NOT NULL
            DEFAULT 'MM/DD/YYYY',
    time_format         time_format_enum        NOT NULL
            DEFAULT '12 Hour',
    measurement_system  measurement_system_enum NOT NULL
            DEFAULT 'Imperial',
    insert_ts           TIMESTAMP               NOT NULL
            DEFAULT CURRENT_TIMESTAMP
);
