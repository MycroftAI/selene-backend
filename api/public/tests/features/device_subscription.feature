Feature: Get the subscription type from the account linked to a device
  Test the endpoint used to fetch the subscription type of a device

  Scenario: User has a free subscription
    When the subscription endpoint is called
    Then free type should be returned
    And the device's last contact time is updated

  Scenario: User has a monthly subscription
    When the subscription endpoint is called for a monthly account
    Then monthly type should be returned
    And the device's last contact time is updated

  Scenario: The endpoint is called to a nonexistent device
    When try to get the subscription for a nonexistent device
    Then 401 status code should be returned for the subscription endpoint
    And the device's last contact time is updated
