import { Component, Input, OnInit } from '@angular/core';

import { Device, DeviceAttribute, DeviceService } from '../../device.service';
import { GeographyEditComponent } from './geography-edit.component';

@Component({
  selector: 'account-device-geography-view',
  templateUrl: './geography-view.component.html',
  styleUrls: ['./geography-view.component.scss']
})
export class GeographyViewComponent implements OnInit {
    @Input() device: Device;
    public deviceGeographies: DeviceAttribute[];
    public dialog = GeographyEditComponent;

    constructor( private service: DeviceService) {
    }

    ngOnInit() {
        this.deviceGeographies = this.service.deviceGeographies;
    }
}
