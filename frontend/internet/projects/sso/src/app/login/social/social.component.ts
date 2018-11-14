import { Component, OnInit } from '@angular/core';

import { faFacebook, faGithub } from '@fortawesome/free-brands-svg-icons';

import { AppService } from '../../app.service';

@Component({
  selector: 'sso-social-login',
  templateUrl: './social.component.html',
  styleUrls: ['./social.component.scss']
})
export class SocialComponent implements OnInit {
    public facebookIcon = faFacebook;
    public githubIcon = faGithub;

    constructor(private authService: AppService) { }

    ngOnInit() { }

    authenticateFacebook(): void {
        this.authService.authenticateWithFacebook();
    }

    authenticateGithub(): void {
        this.authService.authenticateWithGithub();
    }

    authenticateGoogle(): void {
        this.authService.authenticateWithGoogle();
    }


}
