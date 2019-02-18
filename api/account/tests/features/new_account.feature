Feature: Add a new account
  Test the API call to add an account to the database.

  Scenario: Successful account addition
    When a valid new account request is submitted
    Then the request will be successful
     And the account will be added to the system

  Scenario: Request missing a required field
    When a request is sent without an email address
    Then the request will fail with a bad request error
