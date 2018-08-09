import { Component, OnInit, OnDestroy } from '@angular/core';
import { Router } from "@angular/router";
import { Subscription } from "rxjs/internal/Subscription";

import { faCaretDown, faSignInAlt, faSignOutAlt } from "@fortawesome/free-solid-svg-icons";

import { LoginService } from "../login/login.service";
import { HeaderService, User } from "./header.service";

@Component({
    selector: 'market-header',
    templateUrl: './header.component.html',
    styleUrls: ['./header.component.scss']
})
export class HeaderComponent implements OnInit, OnDestroy {
    private loginSubscription: Subscription;
    public signInIcon = faSignInAlt;
    public signOutIcon = faSignOutAlt;
    public menuButtonIcon = faCaretDown;
    public userMenuButtonText: string;
    public isLoggedIn: boolean;

    constructor(
        private loginService: LoginService,
        private router: Router,
        private toolbarService: HeaderService
    ) { }

    ngOnInit() {
        this.loginSubscription = this.loginService.isLoggedIn.subscribe(
            (isLoggedIn) => { this.onLoginStateChange(isLoggedIn) }
        );
        this.loginService.setLoginStatus();
    }

    ngOnDestroy() {
        this.loginSubscription.unsubscribe();
    }

    onLoginStateChange(isLoggedIn) {
        this.isLoggedIn = isLoggedIn;
        if (isLoggedIn) {
            this.toolbarService.getUser().subscribe(
                (user) => {this.userMenuButtonText = user.name}
            );
        }
    }

    login() {
        this.router.navigate(['/login']);
    }

    logout() {
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
}
