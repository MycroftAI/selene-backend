INSERT INTO
    metric.device_activity (
        platform,
        paired
    )
(
    SELECT
        CASE
            WHEN platform IN ('mycroft_mark_1', 'mycroft_mark_2', 'picroft') THEN platform
            ELSE 'other'
        END as product,
        count(*)
    FROM
        device.device
    GROUP BY
        product
)
