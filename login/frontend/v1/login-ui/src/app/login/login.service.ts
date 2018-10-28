import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders} from "@angular/common/http";

import { Observable } from 'rxjs';
import { isArray } from "util";

import { MatSnackBar } from "@angular/material";

export interface AuthResponse {
    expiration: number;
    seleneToken: string;
    tartarusToken: string;
}

export interface SocialLoginData {
    uuid: string;
    accessToken: string;
    refreshToken: string;
    expiration: string;
}

@Injectable()
export class LoginService {
    private antisocialAuthUrl = '/api/antisocial';
    private facebookAuthUrl = '/api/social/facebook';
    private githubAuthUrl = '/api/social/github';
    private googleAuthUrl = '/api/social/google';
    private generateTokensUrl = 'api/social/tokens';

    constructor(private http: HttpClient, public loginSnackbar: MatSnackBar) {
    }

    authorizeAntisocial (username, password): Observable<AuthResponse> {
        let rawCredentials = `${username}:${password}`;
        const codedCredentials = btoa(rawCredentials);
        const httpHeaders = new HttpHeaders(
            {"Authorization": "Basic " + codedCredentials}
        );
        return this.http.get<AuthResponse>(this.antisocialAuthUrl, {headers: httpHeaders})
    }

    authenticateWithFacebook() {
        window.open(this.facebookAuthUrl);
        window.onmessage = (event) => {this.generateSocialLoginTokens(event)};
    }

    authenticateWithGithub() {
        window.open(this.githubAuthUrl);
        window.onmessage = (event) => {this.generateSocialLoginTokens(event)};
    }

    authenticateWithGoogle() {
        window.open(this.googleAuthUrl);
        window.onmessage = (event) => {this.generateSocialLoginTokens(event)};
    }

    generateSocialLoginTokens(event: any) {
        let socialLoginData = this.parseUriParams(event.data);
        if (socialLoginData) {
            this.http.post<AuthResponse>(
                this.generateTokensUrl,
                socialLoginData
            ).subscribe(
                (response) => {this.generateTokenCookies(response)}
            );
        }
        return this.http.post<AuthResponse>(
            this.generateTokensUrl,
            socialLoginData
        )
    }

    parseUriParams (uriParams: string) {
        let socialLoginData: SocialLoginData = null;

        if (uriParams.startsWith('?data=')) {
            let parsedUriParams = JSON.parse(uriParams.slice(6));
            if (isArray(parsedUriParams)) {
                let socialLoginErrorMsg = 'An account exists for the email ' +
                    'address associated with the social network log in ' +
                    'attempt.  To enable log in using a social network, log ' +
                    'in with your username and password and enable the ' +
                    'social network in your account preferences.';
                this.loginSnackbar.open(
                    socialLoginErrorMsg,
                    null,
                    {duration: 30000}
                );
            } else {
                socialLoginData = <SocialLoginData>parsedUriParams;
            }
        }

        return socialLoginData
    }

    generateTokenCookies(authResponse: AuthResponse) {
        let expirationDate = new Date(authResponse.expiration * 1000);
        let domain = document.domain.replace('login.', '');
        document.cookie = 'seleneToken=' + authResponse.seleneToken +
            '; expires=' + expirationDate.toUTCString() +
            '; domain=' + domain;
        document.cookie = 'tartarusToken=' + authResponse.tartarusToken +
            '; expires=' + expirationDate.toUTCString() +
            '; domain=' + domain;
    }


}
