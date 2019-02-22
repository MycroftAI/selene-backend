Feature: Get the subscription type from the account linked to a device
  Test the endpoint used to fetch the subscription type of a device

  Scenario: User has a free subscription
    Given a device pairing code
    When a device is added to an account using the pairing code
    And device is activated
    And the subscription endpoint is called
    Then free type should be returned

  Scenario: User has a monthly subscription
    Given a device pairing code
    When a device is added to an account using the pairing code
    And device is activated
    And the subscription endpoint is called for a monthly account
    Then monthly type should be returned

  Scenario: The endpoint is called to a nonexistent device
    When try to get the subscription for a nonexistent device
    Then 204 status code should be returned for the subscription endpoint