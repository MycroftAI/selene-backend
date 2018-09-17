import { Component, OnInit } from '@angular/core';

import { faFacebook, faGithub } from '@fortawesome/free-brands-svg-icons';

@Component({
    selector: 'login-auth-social',
    templateUrl: './auth-social.component.html',
    styleUrls: ['./auth-social.component.scss']
})
export class AuthSocialComponent implements OnInit {
    public facebookIcon = faFacebook;
    public githubIcon = faGithub;

    constructor() {}

    ngOnInit() { }
}
