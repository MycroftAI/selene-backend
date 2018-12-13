import { Component, OnInit } from '@angular/core';

import { faGithub, IconDefinition } from '@fortawesome/free-brands-svg-icons';

export interface ToggleLabel {
    label: string;
    image?: string;
    icon?: IconDefinition;
}

@Component({
  selector: 'account-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent implements OnInit {
    public socialPlatforms: ToggleLabel[];

  constructor() { }

  ngOnInit() {
      const githubLabel: ToggleLabel = {
          label: 'GitHub Login',
          icon: faGithub
      };
      const googleLabel: ToggleLabel = {
          label: 'Google Login',
          image: '../../assets/google-logo.png'
      };
      const facebookLabel: ToggleLabel = {
          label: 'Facebook Login',
          image: '../../assets/facebook_logo.png'
      };

      this.socialPlatforms = [googleLabel, facebookLabel, githubLabel];
  }

}
