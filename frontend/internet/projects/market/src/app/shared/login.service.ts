import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

import { Observable } from 'rxjs/internal/Observable';
import { Subject } from 'rxjs/internal/Subject';
import { environment } from '../../environments/environment';

const redirectQuery = '?redirect=';
export class User {
    name: string;
}

@Injectable()
export class LoginService {
    public isLoggedIn = new Subject<boolean>();
    public loginUrl: string = environment.loginUrl + '/login';
    private logoutUrl = environment.loginUrl + '/logout';
    private userUrl = '/api/user';

    constructor(private http: HttpClient) {
    }

    getUser(): Observable<User> {
        return this.http.get<User>(this.userUrl);
    }

    setLoginStatus(): void {
        const cookies = document.cookie;
        const seleneTokenExists = cookies.includes('seleneToken');
        const seleneTokenEmpty = cookies.includes('seleneToken=""');
        this.isLoggedIn.next( seleneTokenExists && !seleneTokenEmpty);
    }

    login(): void {
        window.location.assign(this.loginUrl + redirectQuery + window.location.href);
    }

    logout(): void {
        window.location.assign(this.logoutUrl + redirectQuery + window.location.href);
    }
}
