import { Injectable } from '@angular/core';
import { HttpClient } from "@angular/common/http";
import { Observable } from "rxjs";

const logoutUrl = '/api/logout';

@Injectable({
  providedIn: 'root'
})
export class LogoutService {

  constructor(private http: HttpClient ) { }

    logout(): Observable<any> {
        return this.http.get(logoutUrl);
    }

    expireTokenCookies(): void {
        let expiration = new Date();
        let domain = document.domain.replace('login.', '');
        document.cookie = 'seleneToken=""' +
            '; expires=' + expiration.toUTCString() +
            '; domain=' + domain;
        document.cookie = 'tartarusToken=""' +
            '; expires=' + expiration.toUTCString() +
            '; domain=' + domain;

  }
}
