import { Injectable } from '@angular/core';

export interface DeviceAttribute {
    id?: string;
    name: string;
    preDefined: boolean;
}

export interface Device {
    coreVersion: string;
    enclosureVersion: string;
    group: DeviceAttribute;
    id: string;
    location: DeviceAttribute;
    name: string;
    placement: DeviceAttribute;
    platform: string;
}

@Injectable({
  providedIn: 'root'
})
export class DeviceService {
    public devices: Device[] = [
        {
            coreVersion: '18.08',
            enclosureVersion: '1.2.3',
            group: {id: '1', name: 'None', preDefined: true},
            id:  'abc-def-ghi',
            location: {id: '1a2b-3c4d-5e6f', name: 'United States, 64101, CST', preDefined: false},
            name: 'Mark',
            placement: {id: 'bbb-bbb-bbb', name: 'Living Room', preDefined: false},
            platform: 'mark-one'
        },
        {
            coreVersion: '18.08',
            enclosureVersion: '1.2.3',
            group: {id: '1', name: 'None', preDefined: true},
            id:  'bcd-efg-hij',
            location: {id: '1a2b-3c4d-5e6f', name: 'United States, 64101, CST', preDefined: false},
            name: 'Marky Mark',
            placement: {id: 'bbb-bbb-bbb', name: 'Kitchen', preDefined: true},
            platform: 'mark-two'
        },
        {
            coreVersion: '18.08',
            enclosureVersion: '1.2.3',
            group: {id: '2', name: 'Parent House', preDefined: false},
            id:  'cde-fgh-ijk',
            location: {id: '1a2b-3c4d-5e6f', name: 'United States, 64101, CST', preDefined: false},
            name: 'American Pie',
            placement: {id: 'ddd-ddd-ddd', name: 'Bedroom', preDefined: true},
            platform: 'picroft'
        },
        {
            coreVersion: '18.08',
            enclosureVersion: '1.2.3',
            group: {id: '2', name: 'Parent House', preDefined: false},
            id:  'def-ghi-jkl',
            location: {id: '1a2b-3c4d-5e6f', name: 'United States, 64101, CST', preDefined: false},
            name: 'Kappa Delta Epsilon',
            placement: {id: 'fff-fff-fff', name: 'Kitchen', preDefined: true},
            platform: 'kde'
        }
    ];

    public deviceGroups: DeviceAttribute[] = [
        { id: '1', name: 'None', preDefined: true},
        { id: null, name: 'Home', preDefined: true},
        { id: null, name: 'Office', preDefined: true},
        { id: '2', name: 'Parent House', preDefined: false}
    ];

    public devicePlacements: DeviceAttribute[] = [
        { id: '1', name: 'None', preDefined: true},
        { id: null, name: 'Bedroom', preDefined: true},
        { id: null, name: 'Kitchen', preDefined: true},
        { id: '2', name: 'Living Room', preDefined: false}
    ];

    public deviceGeographies: DeviceAttribute[] = [
        {id: '1a2b-3c4d-5e6f', name: 'United States, 64101, CST', preDefined: false},
        {id: 'a1b2-c3d4-e5f6', name: 'United Kingdom, ABCDE, BST', preDefined: false}
    ];

    constructor() { }

    deleteDevice(device: Device): void {
        console.log('deleting device... ');
    }
}
