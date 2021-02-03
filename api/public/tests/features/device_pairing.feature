Feature: Pair a device
  Test the device pairing workflow

  Scenario: Pairing code generation
    When a device requests a pairing code
    Then the request will be successful
    And the pairing data is stored in Redis
    And the pairing data is sent to the device

  Scenario: Device Activation
    Given the user completes the pairing process on the web application
    When the device requests to be activated
    Then the request will be successful
    And the activation data is sent to the device
