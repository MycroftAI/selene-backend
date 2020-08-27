SELECT
    id,
    name,
    engine
FROM
    wake_word.wake_word
WHERE
    name in ('hey mycroft', 'hey jarvis', 'hey ezra', 'christopher')
