import { Component, Input, OnInit } from '@angular/core';

import { PrimaryNavItem } from './globalnav.service';
import {
    faLightbulb,
    faRobot,
    faRocket,
    faRss,
    faStore,
    faUserCircle,
    faUsers
} from '@fortawesome/free-solid-svg-icons';

@Component({
    selector: 'globalnav-sidenav',
    templateUrl: './globalnav.component.html',
    styleUrls: ['./globalnav.component.scss']
})

export class GlobalnavComponent implements OnInit {
    public navigationItems: PrimaryNavItem[];
    @Input() environment: any;
    public contactUsUrl: string;
    public mediaKitUrl: string;
    public termsOfUseUrl: string;
    public privacyPolicyUrl: string;
    public isLoggedIn: boolean;

    constructor() {
    }

    ngOnInit() {
        this.buildNavigationItems();
        this.setLoginStatus();
        this.buildAccountNav();
    }

    buildNavigationItems(): void {
        const aboutMycroftNav: PrimaryNavItem = {
            children: [
                {text: 'Team', url: this.environment.wordpressUrl + '/team'},
                {text: 'Careers', url: this.environment.wordpressUrl + '/careers'}
            ],
            icon: faRobot,
            text: 'About Mycroft'
        };
        const blogNav: PrimaryNavItem = {
            icon: faRss,
            text: 'Blog',
            url: this.environment.wordpressUrl + '/blog'
        };
        const communityNav: PrimaryNavItem = {
            children: [
                {text: 'Chat', url: this.environment.chatUrl},
                {text: 'Forum', url: this.environment.forumUrl}
            ],
            icon: faUsers,
            text: 'Community'
        };
        const contributeNav: PrimaryNavItem = {
            children: [
                {text: 'GitHub', url: 'https://github.com/MycroftAI'},
                {text: 'Translate', url: this.environment.translateUrl},
                {text: 'Wake Word Tagger', url: this.environment.accountUrl + '/#/precise'},
                {text: 'Text-to-Speech Tagger', url: this.environment.accountUrl + '/#/deepspeech'}
            ],
            icon: faLightbulb,
            text: 'Contribute'
        };
        const getStartedNav: PrimaryNavItem = {
            children: [
                {text: 'Get Mycroft', url: this.environment.wordpressUrl + '/download'},
                {text: 'Documentation', url: this.environment.wordpressUrl + '/documentation'}
            ],
            icon: faRocket,
            text: 'Get Started'
        };
        const marketplaceNav: PrimaryNavItem = {
            children: [
                {text: 'Skills', url: this.environment.marketplaceUrl + '/skills'},
                {text: 'Hardware', url: this.environment.wordpressUrl + '/shop'}
            ],
            icon: faStore,
            text: 'Marketplace'
        };

        this.navigationItems = [
            aboutMycroftNav,
            getStartedNav,
            blogNav,
            communityNav,
            contributeNav,
            marketplaceNav,
        ];
        this.contactUsUrl = this.environment.wordpressUrl + '/contact';
        this.mediaKitUrl = this.environment.wordpressUrl + '/media';
        this.privacyPolicyUrl = this.environment.accountUrl + '/#/privacy-policy';
        this.termsOfUseUrl = this.environment.accountUrl + '/#/terms-of-use';
    }

    setLoginStatus(): void {
        const cookies = document.cookie;
        const seleneTokenExists = cookies.includes('seleneToken');
        const seleneTokenEmpty = cookies.includes('seleneToken=""');
        this.isLoggedIn = seleneTokenExists && !seleneTokenEmpty;
    }

    buildAccountNav() {
        const accountNav: PrimaryNavItem = {
            icon: faUserCircle,
            text: 'My Account'
        };
        if (this.isLoggedIn) {
            accountNav.children = [
                {text: 'Devices', url: this.environment.accountUrl + '/#/device'},
                {text: 'Profile', url: this.environment.accountUrl + '/#/profile'},
                {text: 'Skill Settings', url: this.environment.accountUrl + '/#/skill'},
                {text: 'Subscription', url: this.environment.accountUrl + '/#/account'},
                {text: 'User Settings', url: this.environment.accountUrl + '/#/setting/basic'},
                {text: 'Logout', url: this.environment.singleSignOnUrl + '/logout?redirect=' + window.location.href}
            ];
        } else {
            accountNav.children = [
                {text: 'Log In', url: this.environment.singleSignOnUrl + '/login?redirect=' + window.location.href},
                {text: 'Sign Up', url: this.environment.singleSignOnUrl + '/signup'}
            ];
        }
        this.navigationItems.push(accountNav);
    }
}
