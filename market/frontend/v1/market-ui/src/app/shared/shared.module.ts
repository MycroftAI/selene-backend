import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { LoginService } from "./login.service";
import { MaterialModule } from "./material.module";

@NgModule({
    imports: [ CommonModule ],
    exports: [ MaterialModule ],
    providers: [ LoginService ]
})
export class SharedModule { }
