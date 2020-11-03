-- Entities that apply tags to files.
CREATE TABLE tagging.tagger (
    id              uuid                PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type     tagger_type_enum    NOT NULL,
    entity_id       text                NOT NULL,
    insert_ts       TIMESTAMP           NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (entity_type, entity_id)
);
