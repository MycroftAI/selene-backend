import { Component, OnInit } from '@angular/core';

import { faFacebook, faGithub } from "@fortawesome/free-brands-svg-icons";

import { LoginService } from "../login.service";

@Component({
  selector: 'login-social',
  templateUrl: './social.component.html',
  styleUrls: ['./social.component.scss']
})
export class SocialComponent implements OnInit {
    public facebookIcon = faFacebook;
    public githubIcon = faGithub;

  constructor(private authService: LoginService) { }

  ngOnInit() {
  }
    authenticateFacebook(): void {
        this.authService.authenticateWithFacebook()
    }

    authenticateGithub(): void {
        this.authService.authenticateWithGithub();
    }

    authenticateGoogle(): void {
        this.authService.authenticateWithGoogle();
    }


}
