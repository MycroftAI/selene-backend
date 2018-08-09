import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

import { Observable } from 'rxjs';

export class User {
    name: string;
}
@Injectable()
export class HeaderService {
    private userUrl = '/api/user';

    constructor(private http: HttpClient) { }

    getUser(): Observable<User> {
        return this.http.get<User>(this.userUrl)
    }

}
