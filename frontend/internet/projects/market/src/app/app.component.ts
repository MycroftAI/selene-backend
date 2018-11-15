import { Component, OnInit } from '@angular/core';

import { AppService } from './app.service';
import { environment } from '../environments/environment';

@Component({
    selector: 'market-root',
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
    public environment = environment;
    public userName = '';

    constructor(private service: AppService) {
    }

    ngOnInit() {
        this.service.setLoginStatus();
        this.getUser();
    }

    getUser() {
        if (this.service.isLoggedIn) {
            this.service.getUser().subscribe(
                (user) => { this.userName = user.name; }
            );
        }

    }
}
