import { Component, Input, OnInit } from '@angular/core';

import { Device, DeviceGroup, DeviceService } from '../../device.service';
import { GroupEditComponent } from './group-edit.component';

@Component({
  selector: 'account-device-group-view',
  templateUrl: './group-view.component.html',
  styleUrls: ['./group-view.component.scss']
})
export class GroupViewComponent implements OnInit {
    @Input() device: Device;
    public deviceGroups: DeviceGroup[];
    public dialog = GroupEditComponent;

    constructor( private service: DeviceService) {
    }

    ngOnInit() {
        this.deviceGroups = this.service.deviceGroups;
    }
}
