INSERT INTO
    metrics.api (url, access_ts, api, account_id, device_id, duration, http_status)
VALUES
    (%(url)s, %(access_ts)s, %(api)s, %(account_id)s, %(device_id)s, %(duration)s, %(http_status)s)
