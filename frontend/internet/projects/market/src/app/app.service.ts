import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

import { Observable } from 'rxjs';

const userUrl = '/api/user';

@Injectable({
  providedIn: 'root'
})
export class AppService {
    public isLoggedIn: boolean;

    constructor(private http: HttpClient) {
    }

    /**
     * API call to retrieve user info to display.
     */
    getUser(): Observable<any> {
        return this.http.get<any>(userUrl);
    }

    setLoginStatus(): void {
        const cookies = document.cookie;
        const seleneTokenExists = cookies.includes('seleneToken');
        const seleneTokenEmpty = cookies.includes('seleneToken=""');
        this.isLoggedIn = seleneTokenExists && !seleneTokenEmpty;
    }
}
