Feature: Device can upload and fetch skills manifest

  Scenario: Device uploads an unchanged manifest
    Given an authorized device
    When a device uploads a skill manifest without changes
    Then the request will be successful
    And the skill manifest on the database is unchanged
    And the device's last contact time is updated

  Scenario: Device uploads a manifest with an updated skill
    Given an authorized device
    When a device uploads a skill manifest with an updated skill
    Then the request will be successful
    And the skill manifest on the database is unchanged
    And the device's last contact time is updated

  Scenario: Device uploads a manifest with a deleted skill
    Given an authorized device
    When a device uploads a skill manifest with a deleted skill
    Then the request will be successful
    And the skill is removed from the manifest on the database
    And the device's last contact time is updated

  Scenario: Device uploads a manifest with a deleted device-specific skill
    Given an authorized device
    And a device-specific skill installed on the device
    When a device uploads a skill manifest with a deleted device-specific skill
    Then the request will be successful
    And the device-specific skill is removed from the manifest on the database
    And the device-specific skill is removed from the database
    And the device's last contact time is updated

  @new_skill
  Scenario: Device uploads a manifest with a new skill
    Given an authorized device
    When a device uploads a skill manifest with a new skill
    Then the request will be successful
    And the skill is added to the database
    And the skill is added to the manifest on the database
    And the device's last contact time is updated

  Scenario: Unauthorized device attempts manifest upload
    Given an unauthorized device
    When a device uploads a skill manifest without changes
    Then the request will fail with an unauthorized error

  Scenario: Device sends a malformed request for manifest
    Given an authorized device
    When a device uploads a malformed skill manifest
    Then the request will fail with a bad request error
