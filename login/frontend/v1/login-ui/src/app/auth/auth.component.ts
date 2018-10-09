import { Component, OnInit } from '@angular/core';

import { faFacebook, faGithub } from "@fortawesome/free-brands-svg-icons";
import { faLock, faUser } from "@fortawesome/free-solid-svg-icons";

import { AuthResponse, AuthService } from "./auth.service";

@Component({
  selector: 'login-authenticate',
  templateUrl: './auth.component.html',
  styleUrls: ['./auth.component.scss']
})
export class AuthComponent implements OnInit {
    public facebookIcon = faFacebook;
    public githubIcon = faGithub;
    public authFailed: boolean;
    public password: string;
    public passwordIcon = faLock;
    public username: string;
    public usernameIcon = faUser;

    constructor(private authService: AuthService) { }

    ngOnInit() { }

    authenticateFacebook(): void {
        this.authService.authenticateWithFacebook()
    }

    authenticateGithub(): void {
        this.authService.authenticateWithGithub();
    }

    authenticateGoogle(): void {
        this.authService.authenticateWithGoogle();
    }
    authorizeUser(): void {
        this.authService.authorizeAntisocial(this.username, this.password).subscribe(
            (response) => {this.onAuthSuccess(response)},
            (response) => {this.onAuthFailure(response)}
        );
    }

    onAuthSuccess(authResponse: AuthResponse) {
        this.authFailed = false;
        this.authService.generateTokenCookies(authResponse);
        window.history.back();
    }

    onAuthFailure(authorizeUserResponse) {
        if (authorizeUserResponse.status === 401) {
            this.authFailed = true;
        }
    }
}
