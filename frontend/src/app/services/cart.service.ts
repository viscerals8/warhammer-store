import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { Cart, CartItem } from '../models/interface.model';

@Injectable({
  providedIn: 'root'
})
export class CartService {
  private apiUrl = `${environment.apiUrl}/cart`;

  constructor(private http: HttpClient) {}

  getCart(): Observable<Cart> {
    return this.http.get<Cart>(this.apiUrl + '/');
  }

  addToCart(productId: number, quantity: number = 1): Observable<CartItem> {
    return this.http.post<CartItem>(this.apiUrl + '/', { product_id: productId, quantity });
  }

  updateCartItem(cartItemId: number, quantity: number): Observable<CartItem> {
    return this.http.put<CartItem>(`${this.apiUrl}/${cartItemId}`, { quantity });
  }

  removeFromCart(cartItemId: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${cartItemId}`);
  }

  clearCart(): Observable<any> {
    return this.http.delete(this.apiUrl + '/');
  }
}
