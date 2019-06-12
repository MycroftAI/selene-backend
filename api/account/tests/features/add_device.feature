Feature: Pair a device
  Test the device add endpoint

  Scenario: Add a device
    Given an account
    And the account is authenticated
    And a device pairing code
    When an API request is sent to add a device
    Then the request will be successful
    And the device is added to the database
    And the pairing code is removed from cache
    And the pairing token is added to cache
