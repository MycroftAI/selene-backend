Feature: Upload and fetch skills manifest

  Scenario: A skill manifest is successfully uploaded
    Given a device with a skill
    When a skill manifest is uploaded
    Then the skill manifest endpoint should return 200 status code
    And the skill manifest should be added