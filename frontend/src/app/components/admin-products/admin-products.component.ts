import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { ProductService } from '../../services/product.service';
import { NotificationService } from '../../services/notification.service';
import { Product } from '../../models/interface.model';
import { ProductFormComponent } from '../product-form/product-form.component';

@Component({
  selector: 'app-admin-products',
  templateUrl: './admin-products.component.html',
  styleUrls: ['./admin-products.component.css']
})
export class AdminProductsComponent implements OnInit {
  products: Product[] = [];
  loading = false;

  constructor(
    private productService: ProductService,
    private dialog: MatDialog,
    private notify: NotificationService
  ) {}

  ngOnInit(): void {
    this.loadProducts();
  }

  loadProducts(): void {
    this.loading = true;
    this.productService.getProducts().subscribe({
      next: (products: Product[]) => {
        this.products = products;
        this.loading = false;
      },
      error: (err: any) => {
        console.error('Failed to load products', err);
        this.loading = false;
      }
    });
  }

  openProductForm(product?: Product): void {
    const dialogRef = this.dialog.open(ProductFormComponent, {
      width: '700px',
      data: { product }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        if (product) {
          this.productService.updateProduct(product.id, result).subscribe({
            next: () => {
              this.loadProducts();
              this.notify.success('Producto actualizado con exito');
            },
            error: (err: any) => {
              console.error('Failed to update product', err);
              this.notify.error('No se pudo actualizar el producto');
            }
          });
        } else {
          this.productService.createProduct(result).subscribe({
            next: () => {
              this.loadProducts();
              this.notify.success('Producto creado con exito');
            },
            error: (err: any) => {
              console.error('Failed to create product', err);
              this.notify.error('No se pudo crear el producto');
            }
          });
        }
      }
    });
  }

  editProduct(product: Product): void {
    this.openProductForm(product);
  }

  deleteProduct(id: number): void {
    this.notify.confirm({
      title: 'Eliminar producto',
      message: 'Esta seguro que quiere eliminar este producto? Esta accion no se puede deshacer.',
      confirmLabel: 'Eliminar'
    }).subscribe(confirmed => {
      if (!confirmed) return;
      this.productService.deleteProduct(id).subscribe({
        next: () => {
          this.loadProducts();
          this.notify.success('Producto eliminado');
        },
        error: (err: any) => {
          console.error('Failed to delete product', err);
          this.notify.error('No se pudo eliminar el producto');
        }
      });
    });
  }
}
