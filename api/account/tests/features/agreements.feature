Feature: Get the active Profile Policy agreement
  We need to be able to retrieve an agreement and display it on the web app.

  Scenario: Multiple versions of an agreement exist
     When API request for Privacy Policy is made
     Then version 1 of Privacy Policy is returned
