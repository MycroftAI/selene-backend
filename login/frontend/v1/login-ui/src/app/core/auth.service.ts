import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders} from "@angular/common/http";

import { Observable } from 'rxjs';

@Injectable()
export class AuthService {
    private authUrl = '/api/auth';

    constructor(private http: HttpClient) { }

    authorizeUser (username, password): Observable<Object> {
        let rawCredentials = `${username}:${password}`;
        const codedCredentials = btoa(rawCredentials);
        const httpHeaders = new HttpHeaders(
            {"Authorization": "Basic " + codedCredentials}
        );
        return this.http.get<Object>(this.authUrl, {headers: httpHeaders})
    }
}
