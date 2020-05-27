Feature: Get an utterance
  Test the google STT integration

  @stt
  Scenario: A valid flac audio with a voice record is passed
    When A flac audio with the utterance "tell me a joke" is passed
    Then return the utterance "tell me a joke"
    And the device's last contact time is updated
