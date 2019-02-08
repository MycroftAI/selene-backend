Feature: Manage account profiles
  Test the ability of the account API to retrieve and manage a user's profile
  settings.

  Scenario: Retrieve authenticated user's account
    Given an authenticated user
     When account endpoint is called to get user profile
     Then user profile is returned
