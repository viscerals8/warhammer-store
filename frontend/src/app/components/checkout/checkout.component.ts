import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { CartService } from '../../services/cart.service';
import { OrderService } from '../../services/order.service';
import { AuthService } from '../../services/auth.service';
import { FleetService } from '../../services/fleet.service';
import { NotificationService } from '../../services/notification.service';
import { Cart, DeliveryZone } from '../../models/interface.model';

@Component({
  selector: 'app-checkout',
  templateUrl: './checkout.component.html',
  styleUrls: ['./checkout.component.css']
})
export class CheckoutComponent implements OnInit {
  cart: Cart | null = null;
  checkoutForm: FormGroup;
  loading = false;
  zones: DeliveryZone[] = [];
  selectedZone: DeliveryZone | null = null;

  constructor(
    private cartService: CartService,
    private orderService: OrderService,
    private authService: AuthService,
    private fleetService: FleetService,
    private notify: NotificationService,
    private fb: FormBuilder,
    private router: Router
  ) {
    this.checkoutForm = this.fb.group({
      full_name: ['', Validators.required],
      address_line1: ['', Validators.required],
      address_line2: [''],
      city: ['', Validators.required],
      state: ['', Validators.required],
      postal_code: ['', Validators.required],
      country: ['', Validators.required],
      phone: ['', Validators.required],
      zone_id: [null, Validators.required],
      payment_method: ['credit_card']
    });
  }

  get shippingCost(): number {
    return this.selectedZone?.shipping_cost || 0;
  }

  get grandTotal(): number {
    return (this.cart?.total || 0) + this.shippingCost;
  }

  onZoneChange(zoneId: number): void {
    this.selectedZone = this.zones.find(z => z.id === zoneId) || null;
  }

  goToCart(): void {
    this.router.navigate(['/cart']);
  }

  ngOnInit(): void {
    if (!this.authService.isLoggedIn()) {
      this.router.navigate(['/login']);
      return;
    }
    this.loadCart();
    this.fleetService.getZones().subscribe(zones => this.zones = zones);
  }

  loadCart(): void {
    this.loading = true;
    this.cartService.getCart().subscribe({
      next: (cart) => {
        this.cart = cart;
        this.loading = false;
        if (cart.items.length === 0) {
          this.router.navigate(['/cart']);
        }
      },
      error: (err) => {
        console.error('Failed to load cart', err);
        this.loading = false;
      }
    });
  }

  onSubmit(): void {
    if (this.checkoutForm.invalid) {
      return;
    }

    this.loading = true;
    const shippingAddress = this.checkoutForm.value;

    this.orderService.createOrder(
      shippingAddress,
      shippingAddress.payment_method,
      undefined,
      shippingAddress.zone_id
    ).subscribe({
      next: (order) => {
        this.notify.success('Orden creada con exito! Orden #' + order.id);
        this.router.navigate(['/home']);
      },
      error: (err) => {
        console.error('Failed to create order', err);
        this.notify.error('No se pudo crear la orden: ' + (err.error?.error || 'Error desconocido'));
        this.loading = false;
      }
    });
  }
}
