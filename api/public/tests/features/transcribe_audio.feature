Feature: Transcribe audio data
  Test the integration with audio transcription service providers

  @stt
  Scenario: Transcribe audio using Google
    When Utterance "what time is it" is transcribed using Google's STT API
    Then the request will be successful
    And Google's transcription will be correct
    And the device's last contact time is updated

  @stt
  Scenario: Transcribe audio using Assembly AI
    When Utterance "what time is it" is transcribed using Mycroft's transcription service
    Then the request will be successful
    And the transcription will be returned to the device
    And the device's last contact time is updated
    And the transcription metrics for will be added to the database
