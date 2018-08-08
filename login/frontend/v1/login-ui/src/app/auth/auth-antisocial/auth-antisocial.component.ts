import { Component, OnInit } from '@angular/core';

import { faUser, faLock } from "@fortawesome/free-solid-svg-icons";

import { AuthService } from "../../core/auth.service";

@Component({
  selector: 'login-auth-antisocial',
  templateUrl: './auth-antisocial.component.html',
  styleUrls: ['./auth-antisocial.component.scss']
})
export class AuthAntisocialComponent implements OnInit {
    public authorizationFailed = false;
    public password: string;
    public passwordIcon = faLock;
    public username: string;
    public usernameIcon = faUser;
    public user: Object;

    constructor(private authService: AuthService) { }

    ngOnInit() {
    }

    authorizeUser(): void {
        this.authService.authorizeUser(this.username, this.password).subscribe(
            (response) => {this.onAuthorizationSuccess(response)},
            (response) => {this.onAuthorizationFailure(response)}
        );
    }

    onAuthorizationSuccess(authorizeUserResponse) {
        this.user = authorizeUserResponse;
        this.authorizationFailed = false;
        let expirationDate = new Date(authorizeUserResponse.expiration * 1000);
        let domain = document.domain.replace('login.', '');
        document.cookie = 'seleneToken=' + authorizeUserResponse.seleneToken +
            '; expires=' + expirationDate.toUTCString() +
            '; domain=' + domain;
        document.cookie = 'tartarusToken=' + authorizeUserResponse.tartarusToken +
            '; expires=' + expirationDate.toUTCString() +
            '; domain=' + domain;
        window.parent.postMessage('loggedIn', '*')
    }

    onAuthorizationFailure(authorizeUserResponse) {
        if (authorizeUserResponse.status === 401) {
            this.authorizationFailed = true;
        }
    }
}
