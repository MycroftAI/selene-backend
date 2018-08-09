import { Injectable } from '@angular/core';
import { CanActivate, Router, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { LoginService } from './login/login.service';

@Injectable()
export class AuthGuard implements CanActivate {

    constructor(private loginService: LoginService, private router: Router) { }

    canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): boolean {
        let isLoggedIn = false;
        if (this.loginService.isLoggedIn) {
            isLoggedIn = true;
        }
        this.loginService.redirectUrl = state.url;
        this.router.navigate(['/login']);

        return isLoggedIn;
    }
}