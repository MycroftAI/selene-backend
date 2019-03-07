Feature: Send a metric to the metric service

  Scenario: a metric is sent to the metric endpoint by a valid device
    When the metric is sent
    Then 200 status code should be returned

  Scenario: a metric is sent by an invalid device
    When the metric is sent by an invalid device
    Then metrics endpoint should return 204