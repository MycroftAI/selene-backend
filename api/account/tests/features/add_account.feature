Feature: Add a new account
  Test the API call to add an account to the database.

  Scenario: Successful account addition
    Given a user completes new account setup
    When the new account request is submitted
    Then the request will be successful
    And the account will be added to the system

  Scenario: Request missing a required field
    Given a user completes new account setup
    And user does not specify an email address
    When the new account request is submitted
    Then the request will fail with a bad request error
