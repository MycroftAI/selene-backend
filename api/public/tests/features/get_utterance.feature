Feature: Get an utterance
  Test the google STT integration

  @stt
  Scenario: A valid flac audio with a voice record is passed
    When A flac audio with the utterance "what time is it" is passed
    Then the request will be successful
    And return the utterance "what time is it"
    And the device's last contact time is updated
