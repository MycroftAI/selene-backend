import { Component, OnInit } from '@angular/core';

import { faUser, faLock } from "@fortawesome/free-solid-svg-icons";

import { AuthService, AuthResponse } from "../auth.service";

@Component({
  selector: 'login-auth-antisocial',
  templateUrl: './auth-antisocial.component.html',
  styleUrls: ['./auth-antisocial.component.scss']
})
export class AuthAntisocialComponent implements OnInit {
    public authFailed = false;
    public password: string;
    public passwordIcon = faLock;
    public username: string;
    public usernameIcon = faUser;

    constructor(private authService: AuthService) { }

    ngOnInit() { }

    authorizeUser(): void {
        this.authService.authorizeAntisocial(this.username, this.password).subscribe(
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
        window.history.back();
    }

    onAuthFailure(authorizeUserResponse) {
        if (authorizeUserResponse.status === 401) {
            this.authFailed = true;
        }
    }
}
