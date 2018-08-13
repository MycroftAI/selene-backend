import { Component, OnInit } from '@angular/core';
import { Router }      from '@angular/router';

import { LoginService } from './login.service';


@Component({
    selector: 'mycroft-login',
    templateUrl: './login.component.html',
    styleUrls: ['./login.component.scss']
})
export class LoginComponent implements OnInit {

    constructor(public loginService: LoginService, public router: Router) {
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