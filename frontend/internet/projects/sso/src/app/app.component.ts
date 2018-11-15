import { Component, OnInit } from '@angular/core';


@Component({
  selector: 'sso-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
    title = 'Mycroft Login';
    public socialLoginDataFound = false;

    constructor () {
    }

    ngOnInit () {
        const uriParams = decodeURIComponent(window.location.search);

        if (!window.location.pathname && uriParams) {
            this.socialLoginDataFound = true;
            window.opener.postMessage(uriParams, window.location.origin);
            window.close();
        }
    }

}
