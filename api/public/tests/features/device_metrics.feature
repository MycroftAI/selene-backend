Feature: Save metrics sent to selene from mycroft core

  Scenario: Metric sent by device saved to database
    Given an existing device
    When the metrics endpoint is called
    Then the metric is saved to the database
    And the request will be successful
    And device last contact timestamp is updated

  Scenario: Metric endpoint fails for unauthorized device
    Given a non-existent device
    When the metrics endpoint is called
    Then the request will fail with an unauthorized error
    And device last contact timestamp is updated
