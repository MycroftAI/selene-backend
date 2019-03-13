Feature: Upload and fetch skills
  Test all endpoints related to upload and fetch skill settings

  Scenario: A skill is successfully uploaded and retrieved
    Given a device with skill settings
    When the skill settings are updated
    And the skill settings is fetched
    Then the skill settings should be retrieved with the new values
