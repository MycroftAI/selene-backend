import { Component, OnInit } from '@angular/core';

import { LogoutService } from "./logout.service";

@Component({
    selector: 'login-logout',
    templateUrl: './logout.component.html',
    styleUrls: ['./logout.component.scss']
})
export class LogoutComponent implements OnInit {
    private redirectUri: string;

    constructor(private logoutService: LogoutService) { }

    ngOnInit() {
        this.redirectUri = decodeURIComponent(window.location.search).slice(10);
        this.logoutService.logout().subscribe(
          (response) => {this.onLogoutSuccess()},
        );
    }

    onLogoutSuccess(): void {
        this.logoutService.expireTokenCookies();
        setTimeout(() => { window.location.assign(this.redirectUri) }, 1000);
    }

}
