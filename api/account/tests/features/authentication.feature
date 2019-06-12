Feature: Authentication with JWTs
  Some of the API endpoints contain information that is specific to a user.
  To ensure that information is seen only by the user that owns it, we will
  use a login mechanism coupled with authentication tokens to securely identify
  a user.

  The code executed in these tests is embedded in every view call. These tests
  apply to any endpoint that requires authentication.  These tests are meant to
  be the only place authentication logic needs to be tested.

  Scenario: Request for user data includes valid access token
    Given an account with a valid access token
    When a user requests their profile
    Then the request will be successful
     And the authentication tokens will remain unchanged

  Scenario: Access token expired
    Given an account with an expired access token
     When a user requests their profile
     Then the request will be successful
      And the authentication tokens will be refreshed

  Scenario: Access token missing but refresh token valid
    Given an account with a refresh token but no access token
     When a user requests their profile
     Then the request will be successful
      And the authentication tokens will be refreshed

  Scenario: Both access and refresh tokens expired
    Given an account with expired access and refresh tokens
     When a user requests their profile
     Then the request will fail with an unauthorized error
