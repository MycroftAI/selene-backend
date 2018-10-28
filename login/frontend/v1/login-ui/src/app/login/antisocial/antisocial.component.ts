import { Component, OnInit } from '@angular/core';

import { faLock, faUser } from "@fortawesome/free-solid-svg-icons";

import { AuthResponse, LoginService } from "../login.service";

@Component({
  selector: 'login-antisocial',
  templateUrl: './antisocial.component.html',
  styleUrls: ['./antisocial.component.scss']
})
export class AntisocialComponent implements OnInit {
    public authFailed: boolean;
    public password: string;
    public passwordIcon = faLock;
    private redirectUri: string;
    public username: string;
    public usernameIcon = faUser;

  constructor(private authService: LoginService) { }

  ngOnInit() {
        this.redirectUri = decodeURIComponent(window.location.search).slice(10);
  }

  authorizeUser(): void {
      this.authService.authorizeAntisocial(this.username, this.password).subscribe(
          (response) => {this.onAuthSuccess(response)},
          (response) => {this.onAuthFailure(response)}
      );
  }

  onAuthSuccess(authResponse: AuthResponse): void {
      this.authFailed = false;
      this.authService.generateTokenCookies(authResponse);
      window.location.assign(this.redirectUri);
  }

  onAuthFailure(authorizeUserResponse): void {
      if (authorizeUserResponse.status === 401) {
          this.authFailed = true;
      }
  }

}
