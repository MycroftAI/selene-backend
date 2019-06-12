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

  Scenario: Successful on-boarding with membership
    Given a new account without a membership
     And user with username bar is authenticated
    When a user opts into a membership during on-boarding
    Then the request will be successful
    And the account will be updated with the membership

