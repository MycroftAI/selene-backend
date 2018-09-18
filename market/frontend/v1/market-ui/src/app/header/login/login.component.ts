import { Component, OnInit } from '@angular/core';
import { DomSanitizer, SafeResourceUrl } from "@angular/platform-browser";
import { Router }      from '@angular/router';

import { LoginService } from '../../shared/login.service';
import { environment } from "../../../environments/environment";


@Component({
    selector: 'mycroft-login',
    templateUrl: './login.component.html',
    styleUrls: ['./login.component.scss']
})
export class LoginComponent implements OnInit {
    public loginUrl: SafeResourceUrl;

    constructor(
        public loginService: LoginService,
        public router: Router,
        private sanitizer: DomSanitizer
    )
    {
        this.loginUrl = sanitizer.bypassSecurityTrustResourceUrl(environment.loginUrl);
    }

    ngOnInit() {
        window.onmessage = (event) => {
            this.redirectAfterLogin(event)
        }
    }

    redirectAfterLogin(loginEvent) {
        if (loginEvent.origin.includes('login.mycroft') && loginEvent.data === 'loggedIn') {
            this.loginService.setLoginStatus();
            if (this.loginService.isLoggedIn) {
                let redirect = this.loginService.redirectUrl ? this.loginService.redirectUrl : '/';
                this.router.navigate([redirect]);
            }
        }
    }
}