Feature: Send email to a to the account that owns a device
  Test the email endpoint

  Scenario: an email payload is passed to the email endpoint
    Given a device pairing code
    When a device is added to an account using the pairing code
    And device is activated
    And an email message is sent to the email endpoint
    Then an email should be sent to the user's account that owns the device

  Scenario: an email payload is passed to the the email endpoint using a nonexistent device
    When the email endpoint is called for a nonexistent device
    Then 204 status code should be returned