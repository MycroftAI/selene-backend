Feature: Get device's information
  Test the endpoint to get a device

  Scenario: A valid device entity is returned
    Given a device pairing code
    When a device is added to an account using the pairing code
    And device is activated
    And device is retrieved
    Then a valid device should be returned

  Scenario: Try to get a nonexistent device
    When try to fetch a device that doesn't exist in the database
    Then a 204 status code should be returned