Feature: Manage account profiles
  Test the ability of the account API to retrieve and manage a user's profile
  settings.

  Scenario: Retrieve authenticated user's account
    Given an account with a monthly membership
#    And the account is authenticated
    When a user requests their profile
    Then the request will be successful
    And user profile is returned

  Scenario: user with free account opts into a membership
    Given an account without a membership
    And the account is authenticated
    When a monthly membership is added
    Then the request will be successful
    And the account should have a monthly membership

  Scenario: user opts out monthly membership
    Given an account with a monthly membership
#    And the account is authenticated
    When the membership is cancelled
    Then the request will be successful
    And the account should have no membership

  Scenario: user changes from a monthly membership to yearly membership
    Given an account with a monthly membership
#    And the account is authenticated
    When the membership is changed to yearly
    Then the request will be successful
    And the account should have a yearly membership
