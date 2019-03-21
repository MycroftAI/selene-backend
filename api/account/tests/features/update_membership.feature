Feature: Test the API call to update a membership

  Scenario: user with free account opts into a membership
    Given a user with a free account
    When a monthly membership is added
    And the account is requested
    Then the account should have a monthly membership

  Scenario: user opts out monthly membership
    Given a user with a monthly membership
    When the membership is cancelled
    And the account is requested
    Then the account should have no membership

  Scenario: user changes from a monthly membership to yearly membership
    Given a user with a monthly membership
    When the membership is changed to yearly
    And the account is requested
    Then the account should have a yearly membership