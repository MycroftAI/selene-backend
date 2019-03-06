Feature: Upload and fetch skills
  Test all endpoints related to upload and fetch skill settings

  Scenario: One skill is successfully uploaded and retrieved
    Given a device pairing code
    When a device is added to an account using the pairing code
    And device is activated
    And a skill is uploaded
    And the skill is retrieved
    Then skill uploading returns status 200
    And the skill returned is the same as the skill uploaded