Feature: federated login
  User signs into a selene web app after authenticating with a 3rd party.

  Scenario: User with existing account signs in via Facebook
    Given user "foo@mycroft.ai" authenticates through Facebook
     When single sign on validates the account
     Then the request will be successful
      And response contains authentication tokens

  Scenario: User without account signs in via Facebook
    Given user "bar@mycroft.ai" authenticates through Facebook
     When single sign on validates the account
     Then the request will fail with an unauthorized error
      And the response will contain a "no account found for provided email" error message
