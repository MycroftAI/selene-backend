import { Injectable } from '@angular/core';

import { Subject } from "rxjs/internal/Subject";

@Injectable()
export class LoginService {
    public isLoggedIn = new Subject<boolean>();

    redirectUrl: string;

    setLoginStatus() {
        this.isLoggedIn.next(document.cookie.includes('seleneToken'));
    }
}