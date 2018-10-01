import { Component, OnInit } from '@angular/core';

import { faFacebook, faGithub } from '@fortawesome/free-brands-svg-icons';
import { AuthResponse, AuthService } from "../auth.service";

@Component({
    selector: 'login-auth-social',
    templateUrl: './auth-social.component.html',
    styleUrls: ['./auth-social.component.scss']
})
export class AuthSocialComponent implements OnInit {
    public facebookIcon = faFacebook;
    public githubIcon = faGithub;
    public authFailed: boolean;

    constructor(private authService: AuthService) {}

    ngOnInit() { }

    authenticateFacebook(): void {
        this.authService.authenticateWithFacebook().subscribe(
            (response) => {this.onAuthSuccess(response)},
            (response) => {this.onAuthFailure(response)}
        );
    }

    authenticateGithub(): void {
        this.authService.authenticateWithGithub().subscribe(
            (response) => {this.onAuthSuccess(response)},
            (response) => {this.onAuthFailure(response)}
        );
    }

    authenticateGoogle(): void {
        this.authService.authenticateWithGoogle().subscribe(
            (response) => {this.onAuthSuccess(response)},
            (response) => {this.onAuthFailure(response)}
        );
    }

    onAuthSuccess(authResponse: AuthResponse) {
        this.authFailed = false;
        let expirationDate = new Date(authResponse.expiration * 1000);
        let domain = document.domain.replace('login.', '');
        document.cookie = 'seleneToken=' + authResponse.seleneToken +
            '; expires=' + expirationDate.toUTCString() +
            '; domain=' + domain;
        document.cookie = 'tartarusToken=' + authResponse.tartarusToken +
            '; expires=' + expirationDate.toUTCString() +
            '; domain=' + domain;
        window.parent.postMessage('loggedIn', '*')
    }

    onAuthFailure(authorizeUserResponse) {
        if (authorizeUserResponse.status === 401) {
            this.authFailed = true;
        }
    }
}
