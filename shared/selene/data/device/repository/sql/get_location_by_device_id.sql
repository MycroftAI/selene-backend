SELECT
    json_build_object(
        'latitude', city.latitude,
        'longitude', city.longitude
    ) as coordinate,
    json_build_object(
        'name', timezone.name,
        'code', timezone.name,
        'offset', trunc(timezone.gmt_offset * 60 * 60 * 1000),
        'dstOffset', trunc(timezone.dst_offset * 60 * 60 * 1000)
    ) as timezone,
    json_build_object(
        'name', city.name,
        'state', json_build_object(
            'name', region.name,
            'code', region.region_code,
            'country', json_build_object(
                'name', country.name,
                'code', country.iso_code
            )
        )
    ) as city
FROM
    device.device dev
INNER JOIN
    device.geography geo ON dev.geography_id = geo.id
INNER JOIN
    geography.country country ON geo.country_id = country.id
INNER JOIN
    geography.region region ON geo.region_id = region.id
INNER JOIN
    geography.city city ON geo.city_id = city.id
INNER JOIN
    geography.timezone timezone ON geo.timezone_id = timezone.id
WHERE
    dev.id = %(device_id)s