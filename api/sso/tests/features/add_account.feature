Feature: Single Sign On API -- Add a new account
  Test the API call to add an account to the database.

  Scenario: Successful account addition
    Given a user completes new account setup
    When the new account request is submitted
    Then the request will be successful
    And the account will be added to the system
    And the new account will be reflected in the account activity metrics

  Scenario: User enters email address belonging to an existing account
    When a user enters an email address already in use
    Then a duplicate email address error is returned

  Scenario Outline: Request missing a required field
    Given a user completes new account setup
    And user does not include <required field>
    When the new account request is submitted
    Then the request will fail with a bad request error
    And the response will contain a error message

  Examples:
    | required field             |
    | an email address           |
    | a password                 |
    | an accepted Terms of Use   |
    | an accepted Privacy Policy |

  Scenario Outline: Required agreement not accepted
    Given a user completes new account setup
    And user does not agree to the <agreement>
    When the new account request is submitted
    Then the request will fail with a bad request error
    And the response will contain a error message

  Examples:
    | agreement      |
    | Terms of Use   |
    | Privacy Policy |
