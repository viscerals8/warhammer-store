import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { ProductService } from '../../services/product.service';
import { CartService } from '../../services/cart.service';
import { NotificationService } from '../../services/notification.service';
import { Product } from '../../models/interface.model';
import { warhammerPlaceholders } from '../../utils/warhammer-images';

@Component({
  selector: 'app-product-detail',
  templateUrl: './product-detail.component.html',
  styleUrls: ['./product-detail.component.css']
})
export class ProductDetailComponent implements OnInit {
  product!: Product;
  loading = true;
  quantity = 1;
  mainImage: string = '';

  constructor(
    private route: ActivatedRoute,
    private productService: ProductService,
    private cartService: CartService,
    private notify: NotificationService,
    private router: Router
  ) {}

  ngOnInit(): void {
    const id = this.route.snapshot.params['id'];
    this.loadProduct(id);
  }

  loadProduct(id: number): void {
    this.loading = true;
    this.productService.getProduct(id).subscribe({
      next: (product) => {
        this.product = product;
        this.mainImage = this.getImageForProduct(product);
        this.loading = false;
      },
      error: (err) => {
        console.error('Failed to load product', err);
        this.loading = false;
        this.router.navigate(['/products']);
      }
    });
  }

  getImageForProduct(product: Product): string {
    if (product.image_urls && product.image_urls.length > 0) {
      return product.image_urls[0];
    }
    return warhammerPlaceholders[product.id % warhammerPlaceholders.length];
  }

  addToCart(): void {
    if (this.product.stock_quantity < this.quantity) {
      this.notify.error('No hay suficiente stock disponible!');
      return;
    }
    this.cartService.addToCart(this.product.id, this.quantity).subscribe({
      next: () => {
        this.notify.success('Producto agregado al carrito!');
        this.router.navigate(['/cart']);
      },
      error: (err) => {
        console.error('Failed to add to cart', err);
        this.notify.error('No se pudo agregar al carrito: ' + (err.error?.error || 'Error desconocido'));
      }
    });
  }

  goBack(): void {
    this.router.navigate(['/products']);
  }

  increaseQuantity(): void {
    if (this.quantity < this.product.stock_quantity) {
      this.quantity++;
    }
  }

  decreaseQuantity(): void {
    if (this.quantity > 1) {
      this.quantity--;
    }
  }
}
