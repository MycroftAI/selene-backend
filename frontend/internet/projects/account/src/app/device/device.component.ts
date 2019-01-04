import { Component, OnInit } from '@angular/core';
import {MatDialog} from '@angular/material';

import { faCogs, faPlusCircle, faCaretRight, faTrash } from '@fortawesome/free-solid-svg-icons';

import { DeviceGroupComponent } from './device-group/device-group.component';
import {DeviceService, Device, DevicePlacement} from './device.service';
import {DevicePlacementComponent} from './device-placement/device-placement.component';

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
    public productIcons = {
        'mark-one': '../assets/mark-1-icon.svg',
        'mark-two': '../assets/mark-2-icon.svg',
        'picroft': '../assets/picroft-icon.svg',
        'kde': '../assets/kde-icon.svg',
    };
    public editIcon = faCaretRight;
    public settingsIcon = faCogs;
    private selectedDevice: Device;

    constructor(public dialog: MatDialog, private deviceService: DeviceService) { }

    ngOnInit() {
      this.devices = this.deviceService.devices;
    }

    onGroupClick (device: Device) {
        const groupDialogRef = this.dialog.open(DeviceGroupComponent, {data: device.group.name});
        this.selectedDevice = device;
        groupDialogRef.afterClosed().subscribe(
            (result) => { this.updateDeviceGroup(result); }
        );
    }

    updateDeviceGroup(newGroup: string): void {
        this.deviceService.deviceGroups.forEach(
            (group) => {
                if (group.name === newGroup) {
                    this.selectedDevice.group = group;
                }
            }
        );
    }

    onPlacementClick (device: Device) {
        const placementDialogRef = this.dialog.open(DevicePlacementComponent, {data: device.placement.name});
        this.selectedDevice = device;
        placementDialogRef.afterClosed().subscribe(
            (result) => { this.updateDevicePlacement(result); }
        );
    }

    updateDevicePlacement(newPlacement: string): void {
        this.deviceService.devicePlacements.forEach(
            (placement) => {
                if (placement.name === newPlacement) {
                    this.selectedDevice.placement = placement;
                }
            }
        );
    }
}
