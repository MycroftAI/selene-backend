import { Component, OnInit } from '@angular/core';
import { MatSnackBar } from '@angular/material';
import { isArray } from 'util';

import { AppService } from '../app.service';
import { SocialLoginData } from '../app.service';

const noDelay = 0;

@Component({
  selector: 'sso-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent implements OnInit {

    constructor(
        private authService: AppService,
        public loginSnackbar: MatSnackBar
    ) { }

    ngOnInit() {
        this.storeRedirectUrl();
    }

    storeRedirectUrl() {
        const uriQuery = decodeURIComponent(window.location.search);
        if (uriQuery.startsWith('?data')) {
            this.parseUriQuery(uriQuery);
        } else if (uriQuery.startsWith('?redirect')) {
            localStorage.setItem(
                'redirect',
                decodeURIComponent(window.location.search).slice(10)
            );
        }
    }

    parseUriQuery (uriQuery: string) {
        let socialLoginData: SocialLoginData = null;
        const parsedQuery = JSON.parse(uriQuery.slice(6));
        if (isArray(parsedQuery)) {
            const firstItem = parsedQuery[0];
            if (firstItem.key === 'duplicated.user.email') {
                const socialLoginErrorMsg = 'An account exists for the email ' +
                    'address associated with the social network log in ' +
                    'attempt.  To enable log in using a social network, log ' +
                    'in with your username and password and enable the ' +
                    'social network in your account preferences.';
                this.loginSnackbar.open(
                    socialLoginErrorMsg,
                    null,
                    {duration: 30000}
                );
            }
        } else {
            socialLoginData = <SocialLoginData>parsedQuery;
            this.authService.generateSocialLoginTokens(socialLoginData).subscribe(
                (response) => {
                    this.authService.generateTokenCookies(response);
                    this.authService.navigateToRedirectURI(noDelay);
                }
            );
        }
    }
}
