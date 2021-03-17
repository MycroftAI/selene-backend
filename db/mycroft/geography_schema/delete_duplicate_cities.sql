DELETE FROM
    geography.city
WHERE
    id IN %(city_ids)s
    and (population is null or population != %(max_population)s)
