Feature: Pair a device
  Test the device pairing workflow

  Scenario: Device activation
    When a device requests a pairing code
    And the device is added to an account using the pairing code
    And the device is activated
    Then the pairing code request is successful
    And the device activation request is successful
