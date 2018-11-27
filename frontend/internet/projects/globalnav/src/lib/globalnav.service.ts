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

export interface User {
    name: string;
}

export function expireTokenCookies(): void {
    const expiration = new Date();
    const cookieDomain: string = document.domain.replace('market.', '');

    document.cookie = 'seleneToken=""' +
        '; expires=' + expiration.toUTCString() +
        '; domain=' + cookieDomain;
    document.cookie = 'tartarusToken=""' +
        '; expires=' + expiration.toUTCString() +
        '; domain=' + cookieDomain;
}

export function setLoginStatus(): boolean {
    const cookies = document.cookie;
    const seleneTokenExists = cookies.includes('seleneToken');
    const seleneTokenEmpty = cookies.includes('seleneToken=""');
    return seleneTokenExists && !seleneTokenEmpty;
}
