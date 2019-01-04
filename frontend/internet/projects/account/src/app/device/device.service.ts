import { Injectable } from '@angular/core';

export interface DeviceGroup {
    id?: string;
    name: string;
    userDefined: boolean;
}

export interface DeviceLocation {
    id: string;
    region: string;
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
    location: DeviceLocation;
    name: string;
    placement: DevicePlacement;
    product: string;
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
            location: {id: 'aaa-aaa-aaa', region: 'Kansas City, MO'},
            name: 'Mark',
            placement: {id: 'bbb-bbb-bbb', name: 'Living Room', userDefined: true},
            product: 'mark-one'
        },
        {
            coreVersion: '18.08',
            enclosureVersion: '1.2.3',
            group: {id: '1', name: 'None', userDefined: false},
            id:  'bcd-efg-hij',
            location: {id: 'aaa-aaa-aaa', region: 'Kansas City, MO'},
            name: 'Marky Mark',
            placement: {id: 'bbb-bbb-bbb', name: 'Kitchen', userDefined: false},
            product: 'mark-two'
        },
        {
            coreVersion: '18.08',
            enclosureVersion: '1.2.3',
            group: {id: '2', name: 'Parent House', userDefined: true},
            id:  'cde-fgh-ijk',
            location: {id: 'ccc-ccc-ccc', region: 'Baltimore, MD'},
            name: 'American Pie',
            placement: {id: 'ddd-ddd-ddd', name: 'Bedroom', userDefined: false},
            product: 'picroft'
        },
        {
            coreVersion: '18.08',
            enclosureVersion: '1.2.3',
            group: {id: '2', name: 'Parent House', userDefined: true},
            id:  'def-ghi-jkl',
            location: {id: 'eee-eee-eee', region: 'Baltimore, MD'},
            name: 'Kappa Delta Epsilon',
            placement: {id: 'fff-fff-fff', name: 'Kitchen', userDefined: false},
            product: 'kde'
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

    constructor() { }

    deleteDevice(device: Device): void {
        console.log('deleting device... ');
    }
}
