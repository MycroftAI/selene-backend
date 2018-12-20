import { Component, OnInit } from '@angular/core';

import { icon, latLng, marker, tileLayer } from 'leaflet';
import { LatLng, Marker } from 'leaflet';

const streetMaps = tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    detectRetina: true,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
});

const markerIcon = icon({
    iconSize: [ 25, 41 ],
    iconAnchor: [ 13, 41 ],
    iconUrl: 'leaflet/marker-icon.png',
    shadowUrl: 'leaflet/marker-shadow.png'
});

@Component({
    selector: 'account-personal',
    templateUrl: './personal.component.html',
    styleUrls: ['./personal.component.scss']
})
export class PersonalComponent implements OnInit {
    // Default user location to the Kansas City office for users that have not specified
    public userLocation: Marker = marker([ 39.0572, -94.5825 ], { draggable: true, icon: markerIcon });
    public userCoordinate: LatLng;
    public leafletOptions = {
        layers: [ streetMaps, this.userLocation ],
        zoom: 7,
        center: latLng([ 39.1139, -94.5284 ])
    };

    constructor() { }

    ngOnInit() {
        this.userLocation.on('dragend', () => { this.userCoordinate = this.userLocation.getLatLng(); });
        // this.leafletOptions.layers.push(this.userLocation);
    }
}
