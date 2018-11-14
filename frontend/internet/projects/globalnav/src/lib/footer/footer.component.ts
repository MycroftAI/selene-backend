import { Component, Input, OnInit } from '@angular/core';

import {
    faFacebook,
    faInstagram,
    faLinkedin,
    faMedium,
    faReddit,
    faTelegram,
    faTwitter,
    faYoutube,
} from '@fortawesome/free-brands-svg-icons';

@Component({
  selector: 'globalnav-footer',
  templateUrl: './footer.component.html',
  styleUrls: ['./footer.component.scss']
})
export class FooterComponent implements OnInit {
    @Input() contactUsUrl: string;
    @Input() mediaKitUrl: string;
    @Input() privacyPolicyUrl: string;
    public socialMediaIcons = [
        {icon: faTwitter, url: 'https://twitter.com/mycroft_ai'},
        {icon: faFacebook, url: 'https://www.facebook.com/aiforeveryone/'},
        {icon: faInstagram, url: 'https://www.instagram.com/mycroft_ai/'},
        {icon: faYoutube, url: 'https://www.youtube.com/channel/UC1dlmB1lup9RwFQBSGnhA-g'},
        {icon: faTelegram, url: 'https://t.me/mycroft_ai'},
        {icon: faReddit, url: 'https://www.reddit.com/r/Mycroftai/'},
        {icon: faLinkedin, url: 'https://www.linkedin.com/company/mycroft-a.i./'},
        {icon: faMedium, url: 'https://medium.com/@mycroftai'}
    ];
    @Input() termsOfUseUrl: string;

    constructor() { }

    ngOnInit() {
    }

    navigateToSocialMedia(url) {
        window.location.assign(url);
    }

    navigateToTermsOfUse() {
        window.location.assign(this.termsOfUseUrl);
    }

    navigateToPrivacyPolicy() {
        window.location.assign(this.privacyPolicyUrl);
    }

    navigateToContactUs() {
        window.location.assign(this.contactUsUrl);
    }

    navigateToMediaKit() {
        window.location.assign(this.mediaKitUrl);
    }
}
