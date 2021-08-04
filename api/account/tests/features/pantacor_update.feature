Feature: Interact with the Pantacor API
  Devices that use Pantacor to manage the software running on them have a set of
  additional attributes that can be updated using the Pantacor API

  Scenario: Indicate to user that software update is available
    Given an account
    And the account is authenticated
    And a device using Pantacor for continuous delivery
    And the device has pending deployment from Pantacor
    When the user requests to view the device
    Then the request will be successful
    And the response contains the pending deployment ID

  Scenario: User elects to apply a software update
    Given an account
    And the account is authenticated
    And a device using Pantacor for continuous delivery
    And the device has pending deployment from Pantacor
    When the user selects to apply the update
    Then the request will be successful

  Scenario: User enters invalid SSH key
    Given an account
    And the account is authenticated
    And a device using Pantacor for continuous delivery
    When the user enters a well formed RSA SSH key
    Then the request will be successful
    And the response indicates that the SSH key is properly formatted
