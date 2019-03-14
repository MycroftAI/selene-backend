Feature: Test the API call to update a membership

  Scenario: user with free account opts into a membership
    Given a user with a free account
    When a monthly membership is added
    And the account is requested
    Then the account should have a monthly membership