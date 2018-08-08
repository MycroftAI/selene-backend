import { Component, OnInit } from '@angular/core';

import { faFacebook, faGithub, faGoogle } from '@fortawesome/free-brands-svg-icons';

@Component({
    selector: 'login-auth-social',
    templateUrl: './auth-social.component.html',
    styleUrls: ['./auth-social.component.scss']
})
export class AuthSocialComponent implements OnInit {
    public facebookIcon = faFacebook;
    public githubIcon = faGithub;
    public googleIcon = faGoogle;

  constructor() { }

  ngOnInit() {
  }

}
