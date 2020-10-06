Feature: Upload wake word samples from a device
  Users that opted in to the Open Dataset Agreement will have files containing the audio that
  activated the wake word recognizer uploaded to Mycroft servers for classification and tracking.

  Scenario: Device sends wake word audio file
    When the device uploads a wake word file
    Then the request will be successful
    And the audio file is saved to a temporary directory
    And a reference to the sample is stored in the database

   Scenario: Device sends wake word file for an unknown wake word
    When the device uploads a wake word file for an unknown wake word
    Then the request will be successful
    And the audio file is saved to a temporary directory
    And a reference to the sample is stored in the database

  Scenario: Device sends wake word file with non-unique hash value
    When the hash value of the file being uploaded matches a previous upload
    And the device uploads a wake word file
    Then the request will be successful
    And the audio file is saved to a temporary directory
    And a reference to the sample is stored in the database
