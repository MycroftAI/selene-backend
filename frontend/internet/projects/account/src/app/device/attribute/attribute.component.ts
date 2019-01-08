import { Component, Input, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material';

import { faCaretRight } from '@fortawesome/free-solid-svg-icons';

import { Device, DeviceService } from '../device.service';
import { GeographyComponent } from '../geography/geography.component';
import { GroupComponent } from '../group/group.component';
import { PlacementComponent } from '../placement/placement.component';

export interface DeviceAttribute {
    dialog: any;
    label: string;
    possibleValues: any[];
}

@Component({
  selector: 'account-device-attribute',
  templateUrl: './attribute.component.html',
  styleUrls: ['./attribute.component.scss']
})
export class AttributeComponent implements OnInit {
    @Input() attributeHint: string;
    @Input() attributeName: string;
    @Input() attributeValue: any;
    private deviceAttribute: DeviceAttribute;
    public editIcon = faCaretRight;

    constructor(private dialog: MatDialog, private service: DeviceService) {
    }

    ngOnInit() {
        switch (this.attributeName) {
            case 'group':
                this.deviceAttribute = {
                    label: 'Group',
                    dialog: GroupComponent,
                    possibleValues: this.service.deviceGroups
                };
                break;
            case 'location':
                this.deviceAttribute = {
                    label: 'Geography',
                    dialog: GeographyComponent,
                    possibleValues: this.service.deviceGeographies
                };
                break;
            case 'placement':
                this.deviceAttribute = {
                    dialog: PlacementComponent,
                    label: 'Placement',
                    possibleValues: this.service.devicePlacements
                };
                break;
        }
    }

    onClick() {
        const dialogRef = this.dialog.open(
            this.deviceAttribute.dialog,
            {data: this.attributeValue.name});
        dialogRef.afterClosed().subscribe(
            (result) => { this.updateDevice(result); }
        );
    }

    updateDevice(newValue: string) {
        if (newValue) {
            this.deviceAttribute.possibleValues.forEach(
                (value) => {
                    if (value.name === newValue) {
                        this.attributeValue = value;
                    }
                }
            );
        }
    }
}
