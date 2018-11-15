import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { LogoutComponent } from './logout.component';
import { AppService } from '../app.service';

@NgModule({
    imports: [ CommonModule ],
    declarations: [ LogoutComponent ],
    providers: [ AppService ]
})
export class LogoutModule { }
