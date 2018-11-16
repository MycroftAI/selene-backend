import { Component, OnInit } from '@angular/core';
import { Observable } from 'rxjs';

import { AppService, User } from './app.service';
import { environment } from '../environments/environment';

@Component({
    selector: 'market-root',
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
    public environment = environment;
    public user$: Observable<User>;

    constructor(private service: AppService) {
    }

    ngOnInit() {
        this.service.setLoginStatus();
        this.user$ = this.service.getUser();
    }
}
