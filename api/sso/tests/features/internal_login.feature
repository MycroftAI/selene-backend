Feature: internal login
  User signs into a selene web app with an email address and password (rather
  than signing in with a third party authenticator, like Google).

  Scenario: User signs in with valid email/password combination
    Given user enters email address "foo@mycroft.ai" and password "foo"
     When user attempts to login
     Then login request succeeds
      And response contains authentication tokens

  Scenario: User signs in with invalid email/password combination
    Given user enters email address "foo@mycroft.ai" and password "bar"
     When user attempts to login
     Then login fails with "provided credentials not found" error
