Feature: Device API -- Request device location

  Scenario: Location is successfully retrieved from a device
    When a api call to get the location is done
    Then the location should be retrieved
    And the device's last contact time is updated

  Scenario: Try to get a location using an expired etag
    Given an expired etag from a location entity
    When try to get the location using the expired etag
    Then the location should be retrieved
    And an etag associated with the location should be created
    And the device's last contact time is updated

  Scenario: Try to get a location using a valid etag
    Given a valid etag from a location entity
    When try to get the location using a valid etag
    Then the location endpoint should return 304
    And the device's last contact time is updated
