Feature: Get device's information
  Test the endpoint to get a device

  Scenario: A valid device entity is returned
    When device is retrieved
    Then a valid device should be returned

  Scenario: Try to fetch a device not allowed by the access token
    When try to fetch a not allowed device
    Then a 401 status code should be returned

  Scenario: Try to get a device without passing the access token
    When try to fetch a device without the authorization header
    Then a 401 status code should be returned

  Scenario: Update device information
    When the device is updated
    And device is retrieved
    Then the information should be updated