Feature: Send a metric to the metric service

  Scenario: a metric is sent to the metric endpoint by a valid device
    When the metric is sent
    Then 200 status code should be returned
    And device last contact timestamp is updated

  Scenario: a metric is sent by a not allowed device
    When the metric is sent by a not allowed device
    Then metrics endpoint should return 401
    And device last contact timestamp is updated
