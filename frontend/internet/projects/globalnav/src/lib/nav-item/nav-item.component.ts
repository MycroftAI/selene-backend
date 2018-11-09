import { Component, Input, OnInit } from '@angular/core';

import { NavItem } from '../globalnav.service';

@Component({
  selector: 'globalnav-nav-item',
  templateUrl: './nav-item.component.html',
  styleUrls: ['./nav-item.component.scss']
})
export class NavItemComponent implements OnInit {
    @Input() item: NavItem;
    public navItemStyle: object;

    constructor() {
    }

    ngOnInit() {
        this.buildNavItemStyle();
    }

    buildNavItemStyle() {
        this.navItemStyle = {'width': '100%'};
        if (window.location.href.includes(this.item.url)) {
            this.navItemStyle['background-color'] = '#22a7f0';
            this.navItemStyle['color'] = 'white';
            this.navItemStyle['border-radius'] = '4px';
        }
    }
    navigateToUrl() {
      window.location.assign(this.item.url);
    }

}
