Feature: Manage account profiles
  Test the ability of the account API to retrieve and manage a user's profile
  settings.

  Scenario: Retrieve authenticated user's account
    Given an authenticated user
     When a user requests their profile
     Then the request will be successful
      And user profile is returned
