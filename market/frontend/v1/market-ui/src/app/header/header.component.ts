import { Component, OnInit, OnDestroy } from '@angular/core';
import { Subscription } from "rxjs/internal/Subscription";

import {
    faCaretDown,
    faCircle,
    faSignInAlt,
    faSignOutAlt
} from "@fortawesome/free-solid-svg-icons";

import { LoginService } from "../shared/login.service";

@Component({
    selector: 'market-header',
    templateUrl: './header.component.html',
    styleUrls: ['./header.component.scss']
})
export class HeaderComponent implements OnInit, OnDestroy {
    public isLoggedIn: boolean;
    private loginStatus: Subscription;
    public separatorIcon = faCircle;
    public signInIcon = faSignInAlt;
    public signOutIcon = faSignOutAlt;
    public menuButtonIcon = faCaretDown;
    public userMenuButtonText: string;

    constructor(private loginService: LoginService) { }

    ngOnInit() {
        this.loginStatus = this.loginService.isLoggedIn.subscribe(
            (isLoggedIn) => { this.onLoginStateChange(isLoggedIn) }
        );
        this.loginService.setLoginStatus();
    }

    ngOnDestroy() {
        this.loginStatus.unsubscribe();
    }

    onLoginStateChange(isLoggedIn) {
        this.isLoggedIn = isLoggedIn;
        if (isLoggedIn) {
            this.loginService.getUser().subscribe(
                (user) => {this.userMenuButtonText = user.name}
            );
        }
    }

    login() {
        this.loginService.login();
    }

    logout() {
        this.loginService.logout().subscribe(
            (response) => {
                let expiration = new Date();
                let domain = document.domain.replace('market.', '');
                document.cookie = 'seleneToken=""' +
                    '; expires=' + expiration.toUTCString() +
                    '; domain=' + domain;
                document.cookie = 'tartarusToken=""' +
                    '; expires=' + expiration.toUTCString() +
                    '; domain=' + domain;
                this.loginService.setLoginStatus();
            }
        )
    }
}
