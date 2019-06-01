SELECT
	COUNT(acc) AS total,
	COUNT(acc) FILTER(WHERE acc.insert_ts::DATE >= (CURRENT_DATE - INTERVAL %(start)s)) AS total_new,
	COUNT(acc) FILTER(WHERE acc_mem.account_id IS NULL) as free_total,
	COUNT(mem) FILTER(WHERE mem.rate_period = 'month' AND UPPER(acc_mem.membership_ts_range) IS NULL) AS monthly_total,
	COUNT(mem) FILTER(WHERE mem.rate_period = 'month' AND UPPER(acc_mem.membership_ts_range) IS NULL AND LOWER(acc_mem.membership_ts_range) >= (CURRENT_DATE - INTERVAL %(start)s)) AS monthly_new,
	COUNT(mem) FILTER(WHERE mem.rate_period = 'month' AND UPPER(acc_mem.membership_ts_range) IS NOT NULL AND LOWER(acc_mem.membership_ts_range) >= (CURRENT_DATE - INTERVAL %(start)s)) AS monthly_minus,
	COUNT(mem) FILTER(WHERE mem.rate_period = 'year' AND UPPER(acc_mem.membership_ts_range) IS NULL) AS yearly_total,
	COUNT(mem) FILTER(WHERE mem.rate_period = 'year' AND UPPER(acc_mem.membership_ts_range) IS NULL AND LOWER(acc_mem.membership_ts_range) >= (CURRENT_DATE - INTERVAL %(start)s)) AS yearly_new,
	COUNT(mem) FILTER(WHERE mem.rate_period = 'year' AND UPPER(acc_mem.membership_ts_range) IS NOT NULL AND LOWER(acc_mem.membership_ts_range) >= (CURRENT_DATE - INTERVAL %(start)s)) as yearly_minus,
	COUNT(acc_mem) AS paid_total,
	COUNT(acc_mem) FILTER(WHERE UPPER(acc_mem.membership_ts_range) IS NULL AND LOWER(acc_mem.membership_ts_range) >= (CURRENT_DATE - INTERVAL %(start)s)) AS paid_new,
	COUNT(acc_mem) FILTER(WHERE UPPER(acc_mem.membership_ts_range) IS NOT NULL AND LOWER(acc_mem.membership_ts_range) >= (CURRENT_DATE - INTERVAL %(start)s)) AS paid_minus
FROM
	account.account acc
LEFT JOIN
	account.account_membership acc_mem ON acc.id = acc_mem.account_id
LEFT JOIN
	account.membership mem ON acc_mem.membership_id = mem.id