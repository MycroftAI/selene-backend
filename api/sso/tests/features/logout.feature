Feature: logout
  Regardless of how a user logs in, logging out consists of expiring the
  tokens we use to identify logged-in users.

  Scenario: Logged in user requests logout
    Given user "foo@mycroft.ai" is authenticated
     When user attempts to logout
     Then request is successful
      And response contains expired token cookies
      And refresh token in request is removed from account
