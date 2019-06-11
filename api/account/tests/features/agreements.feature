Feature: Get the active agreements
  We need to be able to retrieve an agreement and display it on the web app.

  Scenario: Multiple versions of an agreement exist
     When API request for Privacy Policy is made
     Then the request will be successful
     And Privacy Policy version 999 is returned


  Scenario: Retrieve Terms of Use
     When API request for Terms of Use is made
     Then the request will be successful
     And Terms of Use version 999 is returned
