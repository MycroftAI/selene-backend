Feature: Device requests email sent to the account holder
  Some skills have the ability to send email upon request.  One example of
  this is the support skill, which emails device diagnostics.

  Scenario: Email sent to account holder
    When a user interaction with a device causes an email to be sent
    Then the request will be successful
    And an email should be sent to the account that owns the device
    And the device's last contact time is updated

  Scenario: Email request sent by unauthorized device
    When an unpaired or unauthenticated device attempts to send an email
    Then the request will fail with an unauthorized error
