import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { DeliveryZone, Vehicle } from '../models/interface.model';

@Injectable({
  providedIn: 'root'
})
export class FleetService {
  private apiUrl = `${environment.apiUrl}/fleet`;

  constructor(private http: HttpClient) {}

  getZones(): Observable<DeliveryZone[]> {
    return this.http.get<DeliveryZone[]>(`${this.apiUrl}/zones`);
  }

  getVehicles(): Observable<Vehicle[]> {
    return this.http.get<Vehicle[]>(`${this.apiUrl}/vehicles`);
  }
}
