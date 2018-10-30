import { Component, OnInit } from '@angular/core';

import { AppService } from "../app.service";

const oneSecond = 1000;

@Component({
    selector: 'login-logout',
    templateUrl: './logout.component.html',
    styleUrls: ['./logout.component.scss']
})
export class LogoutComponent implements OnInit {
    constructor(private appService: AppService) { }

    ngOnInit() {
        this.appService.extractRedirectURI();
        this.appService.logout().subscribe(
          (response) => {this.onLogoutSuccess()},
        );
    }

    onLogoutSuccess(): void {
        this.appService.expireTokenCookies();
        this.appService.navigateToRedirectURI(oneSecond);
    }
}
