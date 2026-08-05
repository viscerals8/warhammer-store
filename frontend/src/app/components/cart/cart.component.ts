import { Component, OnInit } from '@angular/core';
import { CartService } from '../../services/cart.service';
import { NotificationService } from '../../services/notification.service';
import { Router } from '@angular/router';
import { Cart, CartItem } from '../../models/interface.model';

@Component({
  selector: 'app-cart',
  templateUrl: './cart.component.html',
  styleUrls: ['./cart.component.css']
})
export class CartComponent implements OnInit {
  cart: Cart | null = null;
  loading = false;

  constructor(
    private cartService: CartService,
    private notify: NotificationService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadCart();
  }

  loadCart(): void {
    this.loading = true;
    this.cartService.getCart().subscribe({
      next: (cart) => {
        this.cart = cart;
        this.loading = false;
      },
      error: (err) => {
        console.error('Failed to load cart', err);
        this.loading = false;
      }
    });
  }

  updateQuantity(item: CartItem, newQuantity: number): void {
    if (newQuantity <= 0) {
      this.removeItem(item.id);
      return;
    }
    this.cartService.updateCartItem(item.id, newQuantity).subscribe({
      next: () => {
        this.loadCart();
      },
      error: (err) => {
        console.error('Failed to update quantity', err);
      }
    });
  }

  removeItem(cartItemId: number): void {
    this.cartService.removeFromCart(cartItemId).subscribe({
      next: () => {
        this.loadCart();
      },
      error: (err) => {
        console.error('Failed to remove item', err);
      }
    });
  }

  clearCart(): void {
    this.notify.confirm({
      title: 'Vaciar carrito',
      message: 'Esta seguro que quiere vaciar el carrito?',
      confirmLabel: 'Vaciar'
    }).subscribe(confirmed => {
      if (!confirmed) return;
      this.cartService.clearCart().subscribe({
        next: () => {
          this.loadCart();
        },
        error: (err) => {
          console.error('Failed to clear cart', err);
          this.notify.error('No se pudo vaciar el carrito');
        }
      });
    });
  }

  proceedToCheckout(): void {
    if (this.cart && this.cart.items.length > 0) {
      this.router.navigate(['/checkout']);
    }
  }

  continueShopping(): void {
    this.router.navigate(['/products']);
  }
}
