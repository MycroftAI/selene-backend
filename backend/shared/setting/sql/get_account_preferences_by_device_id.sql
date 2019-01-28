SELECT acc_pref.* FROM device.account_preferences acc_pref
INNER JOIN account.account acc ON acc_pref.account_id = acc.id
INNER JOIN device.device dev ON acc.id = dev.account_id
WHERE dev.id = %(device_id)s