import { Component, Input, OnInit } from '@angular/core';

import { faChevronUp, faChevronDown } from '@fortawesome/free-solid-svg-icons';

import { PrimaryNavItem } from '../globalnav.service';

@Component({
    selector: 'globalnav-primary-nav-item',
    templateUrl: './primary-nav-item.component.html',
    styleUrls: ['./primary-nav-item.component.scss']
})
export class PrimaryNavItemComponent implements OnInit {
    public expanded = false;
    public expandIcon = faChevronDown;
    public collapseIcon = faChevronUp;
    @Input() primaryNavItem: PrimaryNavItem;

    constructor() { }

    ngOnInit() {
        this.expandCurrentLocation();
    }

    expandCurrentLocation() {
        if (this.primaryNavItem.children && this.primaryNavItem.children.length) {
            this.primaryNavItem.children.forEach(
                (navItem) => {
                    if (window.location.href.includes(navItem.url)) {
                        this.expanded = true;
                    }
                }
            );
        }
    }

    onItemSelected() {
        if (this.primaryNavItem.children && this.primaryNavItem.children.length) {
            this.expanded = !this.expanded;
        } else {
            window.location.assign(this.primaryNavItem.url);
        }
    }
}
