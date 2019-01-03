import { Component, OnInit } from '@angular/core';
import {MatDialog} from '@angular/material';

import { faCogs, faPlusCircle, faCaretRight, faTrash } from '@fortawesome/free-solid-svg-icons';

import { DeviceGroupComponent } from './device-group/device-group.component';
import { DeviceService, Device } from './device.service';

@Component({
    selector: 'account-device',
    templateUrl: './device.component.html',
    styleUrls: ['./device.component.scss']
})
export class DeviceComponent implements OnInit {
    public addIcon = faPlusCircle;
    public deleteIcon = faTrash;
    public devices: Device[];
    public deviceLocations = [
        'United States, 64101, CST',
        'United Kingdom, ABCDE, BST'
    ];
    public devicePlacements = [
        'Basement',
        'Bedroom',
        'Kitchen',
        'Living Room',
        'Add custom placement...'
    ];
    public editIcon = faCaretRight;
    public settingsIcon = faCogs;

    constructor(public dialog: MatDialog, private deviceService: DeviceService) { }

    ngOnInit() {
      this.devices = this.deviceService.devices;
    }

    onGroupClick (device: Device) {
      const groupDialogRef = this.dialog.open(DeviceGroupComponent, {data: device.group});
      groupDialogRef.afterClosed().subscribe(
          (result) => {
              console.log(result);
              if (result) {
                  device.group = result;
              }
          }
      );
    }
}
