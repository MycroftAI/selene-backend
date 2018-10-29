import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { LogoutComponent } from "./logout.component";
import { LogoutService } from "./logout.service";

@NgModule({
    imports: [ CommonModule ],
    declarations: [ LogoutComponent ],
    providers: [ LogoutService ]
})
export class LogoutModule { }
