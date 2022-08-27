Feature: Single Sign On API -- Logout
  Regardless of how a user logs in, logging out consists of expiring the
  tokens we use to identify logged-in users.

  Scenario: Logged in user requests logout
    Given an authenticated account
     When user attempts to logout
     Then the request will be successful
      And response contains expired token cookies
