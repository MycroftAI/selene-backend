import { Injectable } from '@angular/core';

import { IconDefinition } from '@fortawesome/free-solid-svg-icons';

export interface NavItem {
  text: string;
  url: string;
}

export interface PrimaryNavItem {
  children?: NavItem[];
  icon: IconDefinition;
  text: string;
  url?: string;
}


@Injectable({
  providedIn: 'root'
})
export class GlobalnavService {

    constructor() {
    }
}
