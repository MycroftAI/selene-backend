import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'login-authenticate',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent implements OnInit {
    private redirectUri: string;

    constructor() { }

    ngOnInit() {
        this.redirectUri = decodeURIComponent(window.location.search).slice(10);
    }
}
