import { Injectable } from '@angular/core';

export interface DeviceGroup {
    id?: string;
    name: string;
    userDefined: boolean;
}

export interface DeviceGeography {
    id: string;
    name: string;
}

export interface DevicePlacement {
    id?: string;
    name: string;
    userDefined: boolean;
}

export interface Device {
    coreVersion: string;
    enclosureVersion: string;
    group: DeviceGroup;
    id: string;
    location: DeviceGeography;
    name: string;
    placement: DevicePlacement;
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
            group: {id: '1', name: 'None', userDefined: false},
            id:  'abc-def-ghi',
            location: {id: '1a2b-3c4d-5e6f', name: 'United States, 64101, CST'},
            name: 'Mark',
            placement: {id: 'bbb-bbb-bbb', name: 'Living Room', userDefined: true},
            platform: 'mark-one'
        },
        {
            coreVersion: '18.08',
            enclosureVersion: '1.2.3',
            group: {id: '1', name: 'None', userDefined: false},
            id:  'bcd-efg-hij',
            location: {id: '1a2b-3c4d-5e6f', name: 'United States, 64101, CST'},
            name: 'Marky Mark',
            placement: {id: 'bbb-bbb-bbb', name: 'Kitchen', userDefined: false},
            platform: 'mark-two'
        },
        {
            coreVersion: '18.08',
            enclosureVersion: '1.2.3',
            group: {id: '2', name: 'Parent House', userDefined: true},
            id:  'cde-fgh-ijk',
            location: {id: '1a2b-3c4d-5e6f', name: 'United States, 64101, CST'},
            name: 'American Pie',
            placement: {id: 'ddd-ddd-ddd', name: 'Bedroom', userDefined: false},
            platform: 'picroft'
        },
        {
            coreVersion: '18.08',
            enclosureVersion: '1.2.3',
            group: {id: '2', name: 'Parent House', userDefined: true},
            id:  'def-ghi-jkl',
            location: {id: '1a2b-3c4d-5e6f', name: 'United States, 64101, CST'},
            name: 'Kappa Delta Epsilon',
            placement: {id: 'fff-fff-fff', name: 'Kitchen', userDefined: false},
            platform: 'kde'
        }
    ];

    public deviceGroups: DeviceGroup[] = [
        { id: '1', name: 'None', userDefined: false},
        { id: null, name: 'Home', userDefined: false},
        { id: null, name: 'Office', userDefined: false},
        { id: '2', name: 'Parent House', userDefined: true}
    ];

    public devicePlacements: DevicePlacement[] = [
        { id: '1', name: 'None', userDefined: false},
        { id: null, name: 'Bedroom', userDefined: false},
        { id: null, name: 'Kitchen', userDefined: false},
        { id: '2', name: 'Living Room', userDefined: true}
    ];

    public deviceGeographies: DeviceGeography[] = [
        {id: '1a2b-3c4d-5e6f', name: 'United States, 64101, CST'},
        {id: 'a1b2-c3d4-e5f6', name: 'United Kingdom, ABCDE, BST'}
    ];

    constructor() { }

    deleteDevice(device: Device): void {
        console.log('deleting device... ');
    }
}
