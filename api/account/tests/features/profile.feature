Feature: Manage account profiles
  Test the ability of the account API to retrieve and manage a user's profile
  settings.

  Scenario: Retrieve authenticated user's account
    Given an account with a monthly membership
    When a user requests their profile
    Then the request will be successful
    And user profile is returned

  Scenario: user with free account opts into a membership
    Given an account without a membership
    And the account is authenticated
    When a monthly membership is added
    Then the request will be successful
    And the account should have a monthly membership
    And the new member will be reflected in the account activity metrics

  Scenario: user opts out monthly membership
    Given an account with a monthly membership
    When the membership is cancelled
    Then the request will be successful
    And the account should have no membership
    And the deleted member will be reflected in the account activity metrics

  Scenario: user changes from a monthly membership to yearly membership
    Given an account with a monthly membership
    When the membership is changed to yearly
    Then the request will be successful
    And the account should have a yearly membership

  Scenario: user opts into the open dataset
    Given an account opted out of the Open Dataset agreement
    And the account is authenticated
    When the user opts into the open dataset
    Then the request will be successful
    And the account will have a open dataset agreement
    And the new agreement will be reflected in the account activity metrics

  Scenario: user opts out of the open dataset
    Given an account opted into the Open Dataset agreement
    And the account is authenticated
    When the user opts out of the open dataset
    Then the request will be successful
    And the account will not have a open dataset agreement
    And the deleted agreement will be reflected in the account activity metrics
