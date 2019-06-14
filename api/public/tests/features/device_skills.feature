Feature: Upload and fetch skills
  Test all endpoints related to upload and fetch skill settings

  Scenario: A skill is successfully uploaded and retrieved
    Given a device with skill settings
    When the skill settings are updated
    And the skill settings is fetched
    Then the skill settings should be retrieved with the new values
    And device last contact timestamp is updated

  Scenario: Get a 304 when try to get the device's skills using a valid etag
    Given a device with skill settings
    When the skill settings are fetched using a valid etag
    Then the skill setting endpoint should return 304
    And device last contact timestamp is updated

  Scenario: Get a new etag when try to fetch the skill settings using an expired etag
    Given a device with skill settings
    When the skill settings are fetched using an expired etag
    Then the skill settings endpoint should return a new etag
    And device last contact timestamp is updated

  Scenario: Upload a skill with empty settings
    When a skill with empty settings is uploaded
    Then the endpoint to retrieve the skill should return 200
    And device last contact timestamp is updated
