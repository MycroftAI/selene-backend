Feature: Single Sign On API -- Password reset
  The only way a user can change their password in the single sign on application is
  through the password reset feature.  The user clicks a link in an email sent when a
  password reset is requested.  The link takes the user to a page where they reset
  their password and the change password endpoint is called.

  Scenario: User changes password via the password reset email
    Given a user who authenticates with a password
     When the user changes their password
      And user attempts to login
     Then the request will be successful
