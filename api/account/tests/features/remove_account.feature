Feature: Account API -- Delete an account
  Test the API call to delete an account and all its related data from the database.

  Scenario: Successful account deletion
    Given an account
    And the account is authenticated
    When a user requests to delete their account
    Then the request will be successful
    And the user's account is deleted
    And the deleted account will be reflected in the account activity metrics

  Scenario: Membership removed upon account deletion
    Given an account with a monthly membership
    When a user requests to delete their account
    Then the request will be successful
    And the membership is removed from stripe

  Scenario: Wake word files removed upon account deletion
    Given an account opted into the Open Dataset agreement
    And a wake word sample contributed by the user
    And the account is authenticated
    When a user requests to delete their account
    Then the request will be successful
    And the wake word contributions are flagged for deletion
