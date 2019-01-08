import { Component, Input, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material';

import { faCaretRight } from '@fortawesome/free-solid-svg-icons';

@Component({
  selector: 'account-device-attribute-view',
  templateUrl: './attr-view.component.html',
  styleUrls: ['./attr-view.component.scss']
})
export class AttrViewComponent implements OnInit {
    @Input() editDialog: any;
    @Input() hint: string;
    @Input() label: string;
    @Input() possibleValues: any[];
    @Input() value: any;
    public editIcon = faCaretRight;

    constructor(private dialog: MatDialog) {
    }

    ngOnInit() {
    }

    onClick() {
        const dialogRef = this.dialog.open(this.editDialog, { data: this.value.name });
        dialogRef.afterClosed().subscribe(
            (result) => { this.updateDevice(result); }
        );
    }

    updateDevice(newValue: string) {
        if (newValue) {
            this.possibleValues.forEach(
                (value) => {
                    if (value.name === newValue) {
                        this.value = value;
                    }
                }
            );
        }
    }
}
