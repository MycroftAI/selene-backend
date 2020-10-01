-- Files containing audio data used to train wake word machine learning models.
CREATE TABLE tagging.wake_word_file (
    wake_word_id    uuid    NOT NULL REFERENCES wake_word.wake_word,
    UNIQUE (name)
)
INHERITS (tagging.file);
