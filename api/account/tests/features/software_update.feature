Feature: Apply available software update from Pantacor to a device
  Devices that use Pantacor to manage the software running on them.  If a device
  is setup for manual software updates, there will be a button on the device UI
  the user can push to apply the update.  This test will simulate that behavior.

  Scenario: Indicate to user that software update is available
    Given an account
    And the account is authenticated
    And a device using Pantacor with manual updates enabled
    And the device has pending deployment from Pantacor
    When the user requests to view the device
    Then the request will be successful
    And the response contains the pending deployment ID

  Scenario: User elects to apply a software update
    Given an account
    And the account is authenticated
    And a device using Pantacor with manual updates enabled
    And the device has pending deployment from Pantacor
    When the user selects to apply the update
    Then the request will be successful
