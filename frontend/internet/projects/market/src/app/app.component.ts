import { Component, OnInit } from '@angular/core';

import { environment } from '../environments/environment';

@Component({
    selector: 'market-root',
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
    public environment = environment;

    constructor() {
    }

    ngOnInit() {
    }
}
