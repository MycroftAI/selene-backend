import { Component, Input, OnInit } from '@angular/core';
import { MediaMatcher } from '@angular/cdk/layout';
import { Observable } from 'rxjs';
import {
    faBars,
    faLightbulb,
    faRobot,
    faRocket,
    faRss,
    faSignInAlt,
    faSignOutAlt,
    faStore,
    faUserCircle,
    faUsers
} from '@fortawesome/free-solid-svg-icons';

import {
    expireTokenCookies,
    NavItem,
    PrimaryNavItem,
    setLoginStatus,
    User
} from './globalnav.service';

@Component({
    selector: 'globalnav-sidenav',
    templateUrl: './globalnav.component.html',
    styleUrls: ['./globalnav.component.scss']
})

export class GlobalnavComponent implements OnInit {
    @Input() mycroftUrls: any;
    @Input() user$: Observable<User>;
    public footerItems: NavItem[];
    public isLoggedIn: boolean;
    public signInIcon = faSignInAlt;
    public signOutIcon = faSignOutAlt;
    public menuIcon = faBars;
    public mobileQuery: MediaQueryList;
    public navigationItems: PrimaryNavItem[];
    public userName: string;

    constructor(private media: MediaMatcher) {
        this.mobileQuery = media.matchMedia('(max-width: 600px)');
    }

    ngOnInit() {
        this.isLoggedIn = setLoginStatus();
        this.getUser();
        this.buildNavigationItems();
        this.buildAccountNav();
    }

    getUser() {
        if (this.isLoggedIn) {
            this.user$.subscribe(
                (user) => {
                    if (user.name) {
                        this.userName = user.name;
                    } else {
                        this.userName = 'Logged In';
                    }
                },
                (response) => {
                    if (response.status === 401) {
                        expireTokenCookies();
                        this.isLoggedIn = setLoginStatus();
                    }
                }
            );
        }
    }

    buildNavigationItems(): void {
        const aboutMycroftNav: PrimaryNavItem = {
            children: [
                {text: 'Team', url: this.mycroftUrls.wordpress + '/team'},
                {text: 'Careers', url: this.mycroftUrls.wordpress + '/careers'}
            ],
            icon: faRobot,
            text: 'About Mycroft'
        };
        const blogNav: PrimaryNavItem = {
            icon: faRss,
            text: 'Blog',
            url: this.mycroftUrls.wordpress + '/blog'
        };
        const communityNav: PrimaryNavItem = {
            children: [
                {text: 'Chat', url: this.mycroftUrls.chat},
                {text: 'Forum', url: this.mycroftUrls.forum}
            ],
            icon: faUsers,
            text: 'Community'
        };
        const contributeNav: PrimaryNavItem = {
            children: [
                {text: 'GitHub', url: 'https://github.com/MycroftAI'},
                {text: 'Translate', url: this.mycroftUrls.translate},
                {text: 'Wake Words', url: this.mycroftUrls.account + '/#/precise'},
                {text: 'Speech to Text', url: this.mycroftUrls.account + '/#/deepspeech'},
                {text: 'Mimic', url: this.mycroftUrls.mimic}
            ],
            icon: faLightbulb,
            text: 'Contribute'
        };
        const getStartedNav: PrimaryNavItem = {
            children: [
                {text: 'Get Mycroft', url: this.mycroftUrls.wordpress + '/download'},
                {text: 'Documentation', url: this.mycroftUrls.wordpress + '/documentation'}
            ],
            icon: faRocket,
            text: 'Get Started'
        };
        const marketplaceNav: PrimaryNavItem = {
            children: [
                {text: 'Skills', url: this.mycroftUrls.marketplace + '/skills'},
                {text: 'Hardware', url: this.mycroftUrls.wordpress + '/shop'}
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

        this.footerItems = [
            {text: 'Contact Us', url: this.mycroftUrls.wordpress + '/contact'},
            {text: 'Media Kit', url: this.mycroftUrls.wordpress + '/media'},
            {text: 'Privacy Policy', url: this.mycroftUrls.account + '/#/privacy-policy'},
            {text: 'Terms of Use', url: this.mycroftUrls.account + '/#/terms-of-use'}
        ];
    }

    buildAccountNav() {
        const accountNav: PrimaryNavItem = {
            children: [
                {text: 'Devices', url: this.mycroftUrls.account + '/#/device'},
                {text: 'Profile', url: this.mycroftUrls.account + '/#/profile'},
                {text: 'Skill Settings', url: this.mycroftUrls.account + '/#/skill'},
                {text: 'Subscription', url: this.mycroftUrls.account + '/#/account'},
                {text: 'User Settings', url: this.mycroftUrls.account + '/#/setting/basic'},
                {text: 'Logout', url: this.mycroftUrls.singleSignOn + '/logout?redirect=' + window.location.href}
            ],
            icon: faUserCircle,
            text: 'My Account',
        };

        if (this.isLoggedIn) {
            this.navigationItems.push(accountNav);
        }
    }

    navigateToSignIn() {
        window.location.assign(
            this.mycroftUrls.singleSignOn + '/login?redirect=' + window.location.href
        );
    }

    navigateToSignOut() {
        window.location.assign(
            this.mycroftUrls.singleSignOn + '/logout?redirect=' + window.location.href
        );
    }
}
