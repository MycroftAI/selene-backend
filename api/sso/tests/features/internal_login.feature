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
     Then login fails with "provided credentials not found" error

  Scenario: User with existing account signs in via Facebook
    Given user "devops@mycroft.ai" authenticates through facebook
     When single sign on validates the account
     Then login succeeds

  Scenario: User without account signs in via Facebook
    Given user "foo@mycroft.ai" authenticates through facebook
     When single sign on validates the account
     Then login fails with "account not found" error
