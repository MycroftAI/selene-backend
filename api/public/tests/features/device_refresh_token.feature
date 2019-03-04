Feature: Refresh device token
  Test the endpoint used to refresh the device session login

  Scenario: A valid login session is returned after the refreshing token is performed
    Given a device pairing code
    When a device is added to an account using the pairing code
    And device is activated
    And the session token is refreshed
    Then a valid new session entity should be returned

  Scenario: An error status code is returned after trying to refresh an invalid token
    When try to refresh an invalid refresh token
    Then 401 status code should be returned
