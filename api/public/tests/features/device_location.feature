Feature: Fetch device's location

  Scenario: Location is successfully retrieved from a device
    When a api call to get the location is done
    Then the location should be retrieved