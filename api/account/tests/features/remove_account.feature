Feature: Delete an account
  Test the API call to delete an account and all its related data from the database.

  Scenario: Successful account deletion
    Given an account with a monthly membership
     When the user's account is deleted
     Then the request will be successful
      And the membership is removed from stripe
      And the deleted account will be reflected in the account activity metrics
