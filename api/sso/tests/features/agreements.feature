Feature: Single Sign On API -- Get the active agreements
  We need to be able to retrieve an agreement and display it on the web app.

  Scenario: Retrieve Privacy Policy
     When API request for Privacy Policy is made
     Then the request will be successful
     And the current version of the Privacy Policy agreement is returned


  Scenario: Retrieve Terms of Use
     When API request for Terms of Use is made
     Then the request will be successful
     And the current version of the Terms of Use agreement is returned
