import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

import { Observable } from "rxjs/internal/Observable";
import { Subject } from "rxjs/internal/Subject";

export class User {
    name: string;
}

@Injectable()
export class LoginService {
    public isLoggedIn = new Subject<boolean>();
    public redirectUrl: string;
    private userUrl = '/api/user';

    constructor(private http: HttpClient) { }

    getUser(): Observable<User> {
        return this.http.get<User>(this.userUrl)
    }

    setLoginStatus() {
        this.isLoggedIn.next(document.cookie.includes('seleneToken'));
    }
}