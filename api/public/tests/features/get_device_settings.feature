Feature: Retrieve device's settings
  Test the endpoint used to fetch the settings from a device

    Scenario: Device's setting is returned
    When try to fetch device's setting
    Then a valid setting should be returned

    Scenario: Try to get the settings from a nonexistent device
      When the settings endpoint is a called to a nonexistent device
      Then a 204 status code should be returned for the setting