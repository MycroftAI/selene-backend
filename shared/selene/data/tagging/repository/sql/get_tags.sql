SELECT
    t.id,
    t.name,
    t.title,
    t.instructions,
    json_agg(
        json_build_object(
            'value', tv.value,
            'display', tv.display,
            'id', tv.id
        )
    ) AS values
FROM
    tagging.tag t
    LEFT JOIN tagging.tag_value tv ON t.id = tv.tag_id
GROUP BY
    1, 2, 3, 4
