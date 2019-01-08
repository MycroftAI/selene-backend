import { Component, Input, OnInit } from '@angular/core';

import {Device, DevicePlacement, DeviceService} from '../../device.service';
import { PlacementEditComponent } from './placement-edit.component';

@Component({
  selector: 'account-device-placement-view',
  templateUrl: './placement-view.component.html',
  styleUrls: ['./placement-view.component.scss']
})
export class PlacementViewComponent implements OnInit {
    @Input() device: Device;
    public devicePlacements: DevicePlacement[];
    public dialog = PlacementEditComponent;

    constructor( private service: DeviceService) {
    }

    ngOnInit() {
        this.devicePlacements = this.service.devicePlacements;
    }
}
