import { NgModule } from '@angular/core';
import { FlexLayoutModule } from '@angular/flex-layout';
import { MatButtonModule } from '@angular/material';

import { PageNotFoundComponent } from './page-not-found.component';

@NgModule({
  imports: [
      FlexLayoutModule,
      MatButtonModule
  ],
  declarations: [
      PageNotFoundComponent
  ],
  exports: [
      PageNotFoundComponent
  ]
})
export class PageNotFoundModule { }
