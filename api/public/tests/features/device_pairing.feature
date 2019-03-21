#Feature: Pair a device
#  Test the whole device pairing workflow
#
#  Scenario: A valid login session is returned after the pairing is performed
#    Given a device pairing code
#    When a device is added to an account using the pairing code
#    And device is activated
#    Then a login session should be returned
