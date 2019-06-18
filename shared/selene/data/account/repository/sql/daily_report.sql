SELECT
	COUNT(acc) FILTER(WHERE acc.insert_ts::DATE <= %(end_date)s) AS total,
	COUNT(acc) FILTER(WHERE acc.insert_ts::DATE > %(start_date)s AND acc.insert_ts::DATE <= %(end_date)s) AS total_new,
	COUNT(mem) FILTER(WHERE mem.rate_period = 'month' AND UPPER(acc_mem.membership_ts_range) IS NULL AND LOWER(acc_mem.membership_ts_range)::DATE <= %(end_date)s) AS monthly_total,
	COUNT(mem) FILTER(WHERE mem.rate_period = 'month' AND UPPER(acc_mem.membership_ts_range) IS NULL AND LOWER(acc_mem.membership_ts_range)::DATE > %(start_date)s AND LOWER(acc_mem.membership_ts_range)::DATE <= %(end_date)s) AS monthly_new,
	COUNT(mem) FILTER(WHERE mem.rate_period = 'month' AND UPPER(acc_mem.membership_ts_range) IS NOT NULL AND UPPER(acc_mem.membership_ts_range)::DATE > %(start_date)s AND UPPER(acc_mem.membership_ts_range)::DATE <= %(end_date)s) AS monthly_minus,
	COUNT(mem) FILTER(WHERE mem.rate_period = 'year' AND UPPER(acc_mem.membership_ts_range) IS NULL AND LOWER(acc_mem.membership_ts_range)::DATE <= %(end_date)s) AS yearly_total,
	COUNT(mem) FILTER(WHERE mem.rate_period = 'year' AND UPPER(acc_mem.membership_ts_range) IS NULL AND LOWER(acc_mem.membership_ts_range)::DATE > %(start_date)s AND LOWER(acc_mem.membership_ts_range)::DATE <= %(end_date)s) AS yearly_new,
	COUNT(mem) FILTER(WHERE mem.rate_period = 'year' AND UPPER(acc_mem.membership_ts_range) IS NOT NULL AND UPPER(acc_mem.membership_ts_range)::DATE > %(start_date)s AND UPPER(acc_mem.membership_ts_range)::DATE <= %(end_date)s) as yearly_minus,
	COUNT(acc_mem) FILTER(WHERE UPPER(acc_mem.membership_ts_range) IS NULL AND LOWER(acc_mem.membership_ts_range)::DATE <= %(end_date)s) AS paid_total,
	COUNT(acc_mem) FILTER(WHERE UPPER(acc_mem.membership_ts_range) IS NULL AND LOWER(acc_mem.membership_ts_range)::DATE > %(start_date)s AND LOWER(acc_mem.membership_ts_range)::DATE <= %(end_date)s) AS paid_new,
	COUNT(acc_mem) FILTER(WHERE UPPER(acc_mem.membership_ts_range) IS NOT NULL AND UPPER(acc_mem.membership_ts_range)::DATE > %(start_date)s AND UPPER(acc_mem.membership_ts_range)::DATE <= %(end_date)s) AS paid_minus
FROM
	account.account acc
LEFT JOIN
	account.account_membership acc_mem ON acc.id = acc_mem.account_id
LEFT JOIN
	account.membership mem ON acc_mem.membership_id = mem.id