import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { DashboardStats, TopSellingProduct, MonthlySale } from '../models/interface.model';

@Injectable({
  providedIn: 'root'
})
export class DashboardService {
  private apiUrl = `${environment.apiUrl}/dashboard`;

  constructor(private http: HttpClient) {}

  getStats(): Observable<DashboardStats> {
    return this.http.get<DashboardStats>(this.apiUrl + '/stats');
  }

  getTopSellingProducts(month?: string, limit: number = 10): Observable<TopSellingProduct[]> {
    let params = new HttpParams().set('limit', limit.toString());
    if (month) {
      params = params.set('month', month);
    }
    return this.http.get<TopSellingProduct[]>(this.apiUrl + '/top-products', { params });
  }

  getMonthlySales(year?: number): Observable<MonthlySale[]> {
    let params = new HttpParams();
    if (year) {
      params = params.set('year', year.toString());
    }
    return this.http.get<MonthlySale[]>(this.apiUrl + '/monthly-sales', { params });
  }
}
