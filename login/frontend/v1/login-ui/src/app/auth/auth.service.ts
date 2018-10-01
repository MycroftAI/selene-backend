import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders} from "@angular/common/http";

import { Observable } from 'rxjs';

export class AuthResponse {
    expiration: number;
    seleneToken: string;
    tartarusToken: string;
}

@Injectable()
export class AuthService {
    private antisocialAuthUrl = '/api/antisocial';
    private facebookAuthUrl = '/api/social/facebook';
    private githubAuthUrl = '/api/social/github';
    private googleAuthUrl = '/api/social/google';

    constructor(private http: HttpClient) { }

    authorizeAntisocial (username, password): Observable<AuthResponse> {
        let rawCredentials = `${username}:${password}`;
        const codedCredentials = btoa(rawCredentials);
        const httpHeaders = new HttpHeaders(
            {"Authorization": "Basic " + codedCredentials}
        );
        return this.http.get<AuthResponse>(this.antisocialAuthUrl, {headers: httpHeaders})
    }

    authenticateWithFacebook() {
        return this.http.get<any>(this.facebookAuthUrl)
    }

    authenticateWithGithub() {
        return this.http.get<any>(this.githubAuthUrl)
    }

    authenticateWithGoogle() {
        return this.http.get<any>(this.googleAuthUrl)
    }
}
