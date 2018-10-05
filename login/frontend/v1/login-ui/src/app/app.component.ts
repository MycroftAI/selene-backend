import { Component, OnInit } from '@angular/core';


@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
    title = 'Mycroft Login';
    public socialLoginDataFound: boolean = false;

    constructor () {
    }

    ngOnInit () {
        let uriParams = decodeURIComponent(window.location.search);

        if (uriParams) {
            this.socialLoginDataFound = true;
            window.opener.postMessage(uriParams, window.location.origin);
            window.close();
        }
    }

}
