Feature: federated login
  User signs into a selene web app after authenticating with a 3rd party.

  Scenario: User with existing account signs in via Facebook
    Given user "foo@mycroft.ai" authenticates through facebook
     When single sign on validates the account
     Then the request will be successful
      And response contains authentication tokens

  Scenario: User without account signs in via Facebook
    Given user "bar@mycroft.ai" authenticates through facebook
     When single sign on validates the account
     Then login fails with "no account found for provided email" error
