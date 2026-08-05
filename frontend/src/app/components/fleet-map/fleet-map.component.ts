import { Component, OnInit, OnDestroy, AfterViewInit } from '@angular/core';
import * as L from 'leaflet';
import { FleetService } from '../../services/fleet.service';
import { DeliveryZone, Vehicle } from '../../models/interface.model';

@Component({
  selector: 'app-fleet-map',
  templateUrl: './fleet-map.component.html',
  styleUrls: ['./fleet-map.component.css']
})
export class FleetMapComponent implements OnInit, AfterViewInit, OnDestroy {
  loading = true;
  zones: DeliveryZone[] = [];
  vehicles: Vehicle[] = [];

  private map!: L.Map;
  private vehicleMarkers: Map<number, L.Marker> = new Map();
  private pollHandle: any;

  constructor(private fleetService: FleetService) {}

  ngOnInit(): void {
    this.fleetService.getZones().subscribe(zones => {
      this.zones = zones;
      this.drawZones();
    });
  }

  ngAfterViewInit(): void {
    this.initMap();
    this.pollVehicles();
    this.pollHandle = setInterval(() => this.pollVehicles(), 3000);
  }

  ngOnDestroy(): void {
    if (this.pollHandle) {
      clearInterval(this.pollHandle);
    }
    if (this.map) {
      this.map.remove();
    }
  }

  private initMap(): void {
    this.map = L.map('fleet-map', {
      center: [-33.4489, -70.6693],
      zoom: 11,
      zoomControl: true
    });

    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
      maxZoom: 19
    }).addTo(this.map);

    if (this.zones.length) {
      this.drawZones();
    }
  }

  private drawZones(): void {
    if (!this.map) return;
    this.zones.forEach(zone => {
      L.circle([zone.center_lat, zone.center_lng], {
        radius: zone.radius_km * 1000,
        color: zone.color,
        weight: 2,
        fillColor: zone.color,
        fillOpacity: 0.12
      })
        .bindPopup(`<b>${zone.name}</b><br>Envio: $${zone.shipping_cost.toFixed(2)}`)
        .addTo(this.map);
    });
  }

  private pollVehicles(): void {
    this.fleetService.getVehicles().subscribe(vehicles => {
      this.vehicles = vehicles;
      this.loading = false;
      vehicles.forEach(v => this.upsertVehicleMarker(v));
    });
  }

  private upsertVehicleMarker(vehicle: Vehicle): void {
    const icon = L.divIcon({
      className: 'vehicle-marker',
      html: `<div class="vehicle-pin ${vehicle.status}">&#128666;</div>`,
      iconSize: [34, 34],
      iconAnchor: [17, 17]
    });

    let marker = this.vehicleMarkers.get(vehicle.id);
    if (!marker) {
      marker = L.marker([vehicle.lat, vehicle.lng], { icon }).addTo(this.map);
      marker.bindPopup(this.vehiclePopup(vehicle));
      this.vehicleMarkers.set(vehicle.id, marker);
    } else {
      marker.setLatLng([vehicle.lat, vehicle.lng]);
      marker.setPopupContent(this.vehiclePopup(vehicle));
    }
  }

  private vehiclePopup(vehicle: Vehicle): string {
    return `<b>${vehicle.name}</b><br>Chofer: ${vehicle.driver_name || 'N/A'}<br>Patente: ${vehicle.plate || 'N/A'}<br>Estado: ${vehicle.status}`;
  }
}
