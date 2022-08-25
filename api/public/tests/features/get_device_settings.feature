Feature: Device API -- Request device settings
  Test the endpoint used to fetch the settings from a device

  Scenario: Device's setting is returned
    When try to fetch device's setting
    Then a valid setting should be returned
    And the device's last contact time is updated

  Scenario: Try to get the settings from a not allowed device
    When the settings endpoint is a called to a not allowed device
    Then a 401 status code should be returned for the setting
    And the device's last contact time is updated

  Scenario: Try to get the device's settings using a valid etag
    Given a device's setting with a valid etag
    When try to fetch the device's settings using a valid etag
    Then 304 status code should be returned by the device's settings endpoint
    And the device's last contact time is updated

  Scenario: Try to get a device's settings using a expired etag
    Given a device's setting etag expired by the web ui at device level
    When try to fetch the device's settings using an expired etag
    Then 200 status code should be returned by the device's setting endpoint and a new etag
    And the device's last contact time is updated
