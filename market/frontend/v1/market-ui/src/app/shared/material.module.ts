import { NgModule } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatDialogModule } from "@angular/material/dialog";
import { MatFormFieldModule} from "@angular/material/form-field";
import { MatInputModule} from "@angular/material/input";
import { MatMenuModule } from "@angular/material";
import { MatSelectModule } from "@angular/material/select";
import { MatSnackBarModule } from "@angular/material/snack-bar";
import { MatToolbarModule } from '@angular/material/toolbar';

@NgModule(
    {
        imports: [
            MatButtonModule,
            MatCardModule,
            MatDialogModule,
            MatFormFieldModule,
            MatFormFieldModule,
            MatMenuModule,
            MatSelectModule,
            MatSnackBarModule,
            MatToolbarModule,
        ],
        exports: [
            MatButtonModule,
            MatCardModule,
            MatDialogModule,
            MatFormFieldModule,
            MatInputModule,
            MatMenuModule,
            MatSelectModule,
            MatSnackBarModule,
            MatToolbarModule,
        ]
    }
)

export class MaterialModule { }
