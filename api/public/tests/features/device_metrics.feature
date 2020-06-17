Feature: Save metrics sent to selene from mycroft core

  Scenario: User opted into the open dataset uses their device
    Given a device registered to a user opted into the open dataset
    When someone issues a voice command to the device
    Then usage metrics are saved to the database
    And the device's last contact time is updated
    And the account's last activity time is updated
    And the account activity metrics will be updated

  Scenario: Metric endpoint fails for unauthorized device
    Given a non-existent device
    When someone issues a voice command to the device
    Then the request will fail with an unauthorized error
    And the device's last contact time is updated
