Feature: Pair a device
  Test the device pairing workflow

  Scenario: Pairing code generation
    When a device requests a pairing code
    Then the request will be successful
    And the pairing data is stored in Redis
    And the pairing data is sent to the device

  Scenario: Device activation
    Given the user completes the pairing process on the web application
    When the device requests to be activated
    Then the request will be successful
    And the activation data is sent to the device
    And the device attributes are stored in the database

  Scenario: Pantacor device activation
    Given the user completes the pairing process on the web application
    When a device using Pantacor requests to be activated
    Then the request will be successful
    And the activation data is sent to the device
    And the device attributes are stored in the database
    And the Pantacor device configuration is stored in the database
