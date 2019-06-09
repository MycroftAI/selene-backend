Feature: Save metrics sent to selene from mycroft core

  Scenario: Metric sent by device saved to database
    Given an authorized device
     When the metrics endpoint is called
     Then the metric is saved to the database
      And the request will be successful

  Scenario: Metric endpoint fails for unauthorized device
    Given an unauthorized device
     When the metrics endpoint is called
     Then the request will fail with an unauthorized error
