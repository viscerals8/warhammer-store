import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { Order } from '../models/interface.model';

@Injectable({
  providedIn: 'root'
})
export class OrderService {
  private apiUrl = `${environment.apiUrl}/orders`;

  constructor(private http: HttpClient) {}

  createOrder(shippingAddress: any, paymentMethod?: string, notes?: string, zoneId?: number | null): Observable<Order> {
    return this.http.post<Order>(this.apiUrl + '/', {
      shipping_address: shippingAddress,
      payment_method: paymentMethod,
      notes: notes,
      zone_id: zoneId
    });
  }

  getOrders(): Observable<Order[]> {
    return this.http.get<Order[]>(this.apiUrl + '/');
  }

  getOrder(id: number): Observable<Order> {
    return this.http.get<Order>(`${this.apiUrl}/${id}`);
  }

  getAllOrders(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/admin`);
  }

  updateStatus(orderId: number, status: string): Observable<any> {
    return this.http.put(`${this.apiUrl}/${orderId}/status`, { status });
  }
}
