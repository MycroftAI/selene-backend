import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Router } from "@angular/router";

import { Observable } from "rxjs/internal/Observable";
import { Subject } from "rxjs/internal/Subject";
import { environment } from "../../environments/environment";

export class User {
    name: string;
}

@Injectable()
export class LoginService {
    public isLoggedIn = new Subject<boolean>();
    public redirectUrl: string;
    private logoutUrl = environment.loginUrl + '/api/logout';
    private userUrl = '/api/user';

    constructor(private http: HttpClient, private router: Router) {
    }

    getUser(): Observable<User> {
        return this.http.get<User>(this.userUrl);
    }

    setLoginStatus() {
        let cookies = document.cookie,
            seleneTokenExists = cookies.includes('seleneToken'),
            seleneTokenEmpty = cookies.includes('seleneToken=""');
        this.isLoggedIn.next( seleneTokenExists && !seleneTokenEmpty);
    }

    login() {
        window.location.assign(environment.loginUrl);
    }

    logout(): Observable<any> {
        return this.http.get(this.logoutUrl);
    }
}