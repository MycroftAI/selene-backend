import { Component, OnInit } from '@angular/core';

import { AppService } from '../app.service';

const oneSecond = 1000;

@Component({
    selector: 'sso-logout',
    templateUrl: './logout.component.html',
    styleUrls: ['./logout.component.scss']
})
export class LogoutComponent implements OnInit {
    constructor(private appService: AppService) { }

    ngOnInit() {
        const uriQuery = decodeURIComponent(window.location.search);
        if (uriQuery.startsWith('?redirect')) {
            localStorage.setItem(
                'redirect',
                decodeURIComponent(window.location.search).slice(10)
            );
        }

        this.appService.logout().subscribe(
          (response) => { this.onLogoutSuccess(); },
        );
    }

    onLogoutSuccess(): void {
        this.appService.expireTokenCookies();
        this.appService.navigateToRedirectURI(oneSecond);
    }
}
