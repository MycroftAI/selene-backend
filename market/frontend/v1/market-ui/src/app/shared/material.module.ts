import { NgModule } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatDialogModule } from "@angular/material/dialog";
import { MatDividerModule} from "@angular/material";
import { MatFormFieldModule} from "@angular/material/form-field";
import { MatInputModule} from "@angular/material/input";
import { MatMenuModule } from "@angular/material";
import { MatSelectModule } from "@angular/material/select";
import { MatSnackBarModule } from "@angular/material/snack-bar";
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatTooltipModule } from "@angular/material/tooltip";

@NgModule(
    {
        imports: [
            MatButtonModule,
            MatCardModule,
            MatDialogModule,
            MatDividerModule,
            MatFormFieldModule,
            MatFormFieldModule,
            MatMenuModule,
            MatSelectModule,
            MatSnackBarModule,
            MatToolbarModule,
            MatTooltipModule
        ],
        exports: [
            MatButtonModule,
            MatCardModule,
            MatDialogModule,
            MatDividerModule,
            MatFormFieldModule,
            MatInputModule,
            MatMenuModule,
            MatSelectModule,
            MatSnackBarModule,
            MatToolbarModule,
            MatTooltipModule
        ]
    }
)

export class MaterialModule { }
