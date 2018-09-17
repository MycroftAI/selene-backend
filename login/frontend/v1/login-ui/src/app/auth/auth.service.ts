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
    private antisocialAuthUrl = '/api/auth/antisocial';
    private facebookAuthUrl = '/api/auth/facebook';

    constructor(private http: HttpClient) { }

    authorizeAntisocial (username, password): Observable<AuthResponse> {
        let rawCredentials = `${username}:${password}`;
        const codedCredentials = btoa(rawCredentials);
        const httpHeaders = new HttpHeaders(
            {"Authorization": "Basic " + codedCredentials}
        );
        return this.http.get<AuthResponse>(this.antisocialAuthUrl, {headers: httpHeaders})
    }

    authorizeFacebook(userData: any) {
        const httpHeaders = new HttpHeaders({'token': userData.token});
        return this.http.get<AuthResponse>(this.facebookAuthUrl, {headers: httpHeaders})
    }
}
