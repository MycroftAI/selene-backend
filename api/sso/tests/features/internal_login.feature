Feature: internal login
  User signs into a selene web app with an email address and password (rather
  than signing in with a third party authenticator, like Google).

  Scenario: User signs in with valid email/password combination
    Given user enters email address "devops@mycroft.ai" and password "devops"
     When user attempts to login
     Then login succeeds

  Scenario: User signs in with invalid email/password combination
    Given user enters email address "devops@mycroft.ai" and password "foo"
     When user attempts to login
     Then login fails
