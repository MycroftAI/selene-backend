import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders} from '@angular/common/http';

import { Observable } from 'rxjs';

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

const antisocialAuthUrl = '/api/antisocial';
const facebookAuthUrl = '/api/social/facebook';
const githubAuthUrl = '/api/social/github';
const googleAuthUrl = '/api/social/google';
const generateTokensUrl = 'api/social/tokens';
const logoutUrl = '/api/logout';


@Injectable()
export class AppService {
    private cookieDomain: string = document.domain.replace('login.', '');

    constructor(private http: HttpClient) { }

    navigateToRedirectURI(delay: number): void {
        const redirectURI = localStorage.getItem('redirect');
        localStorage.removeItem('redirect');
        setTimeout(() => { window.location.assign(redirectURI); }, delay);
    }

    authorizeAntisocial (username, password): Observable<AuthResponse> {
        const rawCredentials = `${username}:${password}`;
        const codedCredentials = btoa(rawCredentials);
        const httpHeaders = new HttpHeaders(
            {'Authorization': 'Basic ' + codedCredentials}
        );
        return this.http.get<AuthResponse>(antisocialAuthUrl, {headers: httpHeaders});
    }

    authenticateWithFacebook() {
        window.location.assign(facebookAuthUrl);
    }

    authenticateWithGithub() {
        window.location.assign(githubAuthUrl);
    }

    authenticateWithGoogle() {
        window.location.assign(googleAuthUrl);
    }

    generateSocialLoginTokens(socialLoginData: any) {
        return this.http.post<AuthResponse>(
            generateTokensUrl,
            socialLoginData
        );
    }

    generateTokenCookies(authResponse: AuthResponse) {
        const expirationDate = new Date(authResponse.expiration * 1000);
        document.cookie = 'seleneToken=' + authResponse.seleneToken +
            '; expires=' + expirationDate.toUTCString() +
            '; domain=' + this.cookieDomain;
        document.cookie = 'tartarusToken=' + authResponse.tartarusToken +
            '; expires=' + expirationDate.toUTCString() +
            '; domain=' + this.cookieDomain;
    }

    logout(): Observable<any> {
        return this.http.get(logoutUrl);
    }

    expireTokenCookies(): void {
        const expiration = new Date();
        document.cookie = 'seleneToken=""' +
            '; expires=' + expiration.toUTCString() +
            '; domain=' + this.cookieDomain;
        document.cookie = 'tartarusToken=""' +
            '; expires=' + expiration.toUTCString() +
            '; domain=' + this.cookieDomain;

  }
}
