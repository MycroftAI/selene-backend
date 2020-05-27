Feature: Integration with Wolfram Alpha API

  Scenario: Question sent to the wolfram alpha endpoint
    When a question is sent
    Then the wolfram alpha endpoint should return 200
    And the device's last contact time is updated

  Scenario: Question sent to the wolfram alpha spoken endpoint
    When a question is sent to the wolfram alpha spoken endpoint
    Then the wolfram alpha endpoint should return 200
    And the device's last contact time is updated
