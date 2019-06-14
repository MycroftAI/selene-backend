Feature: Get device's information
  Test the endpoint to get a device

  Scenario: A valid device entity is returned
    When device is retrieved
    Then a valid device should be returned
    And device last contact timestamp is updated

  Scenario: Try to fetch a device not allowed by the access token
    When try to fetch a not allowed device
    Then a 401 status code should be returned
    And device last contact timestamp is updated

  Scenario: Try to get a device without passing the access token
    When try to fetch a device without the authorization header
    Then a 401 status code should be returned
    And device last contact timestamp is updated

  Scenario: Update device information
    When the device is updated
    And device is retrieved
    Then the information should be updated
    And device last contact timestamp is updated

  Scenario: Get a not modified device using etag
    Given a device with a valid etag
    When try to fetch a device using a valid etag
    Then 304 status code should be returned by the device endpoint
    And device last contact timestamp is updated

  Scenario: Get a device using an expired etag
    Given a device's etag expired by the web ui
    When try to fetch a device using an expired etag
    Then should return status 200
    And a new etag
    And device last contact timestamp is updated
