Feature: Add a new account
  Test the API call to add an account to the database.

  Scenario: Successful account addition
    When a valid new account request is submitted
    Then the request will be successful
     And the account will be added to the system
