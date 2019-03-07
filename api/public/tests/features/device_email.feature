Feature: Send email to a to the account that owns a device
  Test the email endpoint

  Scenario: an email payload is passed to the email endpoint
    When an email message is sent to the email endpoint
    Then an email should be sent to the user's account that owns the device

  Scenario: an email payload is passed to the the email endpoint using a not allowed device
    When the email endpoint is called by a not allowed device
    Then 401 status code should be returned by the email endpoint