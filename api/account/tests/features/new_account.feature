Feature: Add a new account
  Test the API call to add an account to the database.

  Scenario: Successful account addition with membership
    Given a user completes on-boarding
      And user opts into a membership
     When the new account request is submitted
     Then the request will be successful
      And the account will be added to the system with a membership

  Scenario: Successful account addition without  membership
    Given a user completes on-boarding
      And user opts out of membership
     When the new account request is submitted
     Then the account will be added to the system without a membership

  Scenario: Request missing a required field
    Given a user completes on-boarding
      And user does not specify an email address
    When the new account request is submitted
    Then the request will fail with a bad request error

