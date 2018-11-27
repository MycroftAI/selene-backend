import { Component, Input, OnInit } from '@angular/core';

import { NavItem } from '../globalnav.service';

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
    @Input() footerItems: NavItem[];
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

    constructor() { }

    ngOnInit() {
    }
}
