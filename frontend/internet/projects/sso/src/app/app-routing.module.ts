import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { LoginComponent } from './login/login.component';
import { LogoutComponent } from './logout/logout.component';
// import { PageNotFoundComponent } from './page-not-found/page-not-found.component';

const routes: Routes = [
    { path: 'profile', component: LoginComponent },
    { path: 'logout', component: LogoutComponent },
    { path: '', redirectTo: '/profile', pathMatch: 'full' },
    // { path: '**', component: PageNotFoundComponent }
];

@NgModule({
    imports: [ RouterModule.forRoot(routes) ],
    exports: [ RouterModule ]
})
export class AppRoutingModule {
}
