Feature: Integration with Wolfram Alpha API
  Mycroft Core uses Wolfram Alpha as a "fallback".  When a user makes a request
  that cannot be satisfied by an installed skill, the fallback system is used to
  attempt to answer the query.  The device API is used as a proxy to anonymize user
  requests.

  Scenario: Mycroft Core fallback system sends query to the Wolfram Alpha
    When a question is sent to the Wolfram Alpha full results endpoint
    Then the answer provided by Wolfram Alpha is returned
    And the device's last contact time is updated
    And the account's last activity time is updated
    And the account activity metrics will be updated

  Scenario: Question sent to the wolfram alpha spoken endpoint
    When a question is sent to the wolfram alpha spoken endpoint
    Then the answer provided by Wolfram Alpha is returned
    And the device's last contact time is updated
