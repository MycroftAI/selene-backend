-- Perform a cascading delete on an account.  All children of the account
-- table should have ON DELETE CASCADE clauses.  If this request fails, a missing
-- ON DELETE CASCADE clause may be the culprit.
DELETE FROM
    account.account
WHERE
    id = %(id)s
