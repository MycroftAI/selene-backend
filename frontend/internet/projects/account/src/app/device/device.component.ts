import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material';

import { faCogs, faPlusCircle, faTrash } from '@fortawesome/free-solid-svg-icons';

import { DeviceService, Device } from './device.service';
import { RemoveComponent } from './remove/remove.component';

@Component({
    selector: 'account-device',
    templateUrl: './device.component.html',
    styleUrls: ['./device.component.scss']
})
export class DeviceComponent implements OnInit {
    public addIcon = faPlusCircle;
    public deleteIcon = faTrash;
    public devices: Device[];
    public platforms = {
        'mark-one': {icon: '../assets/mark-1-icon.svg', displayName: 'Mark I'},
        'mark-two': {icon: '../assets/mark-2-icon.svg', displayName: 'Mark II'},
        'picroft': {icon: '../assets/picroft-icon.svg', displayName: 'Picroft'},
        'kde': {icon: '../assets/kde-icon.svg', displayName: 'KDE'}
    };
    public settingsIcon = faCogs;
    private selectedDevice: Device;

    constructor(public dialog: MatDialog, private deviceService: DeviceService) { }

    ngOnInit() {
      this.devices = this.deviceService.devices;
    }

    onRemovalClick (device: Device) {
        const removalDialogRef = this.dialog.open(RemoveComponent, {data: false});
        this.selectedDevice = device;
        removalDialogRef.afterClosed().subscribe(
            (result) => {
                if (result) { this.deviceService.deleteDevice(device); }
            }
        );
    }

    defineStaticDeviceFields(device: Device) {
        const knownPlatform = this.platforms[device.platform];
        return [
            {name: 'Platform', value: knownPlatform ? knownPlatform.displayName : device.platform},
            {name: 'Core Version', value: device.coreVersion},
            {name: 'Enclosure Version', value: device.enclosureVersion}
        ];
    }

    getDeviceIcon(device: Device) {
        const knownPlatform = this.platforms[device.platform];
        // TODO: get unknown product icon from design team.
        return knownPlatform ? knownPlatform.icon : '../assets/mark-1-icon.svg';
    }
}
