import { Component, Inject, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Product, Category } from '../../models/interface.model';
import { ProductService } from '../../services/product.service';

@Component({
  selector: 'app-product-form',
  templateUrl: './product-form.component.html',
  styleUrls: ['./product-form.component.css']
})
export class ProductFormComponent implements OnInit {
  productForm: FormGroup;
  categories: Category[] = [];
  isEditMode = false;

  constructor(
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<ProductFormComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { product?: Product },
    private productService: ProductService
  ) {
    this.isEditMode = !!data?.product;
    this.productForm = this.fb.group({
      name: ['', Validators.required],
      description: [''],
      price: [0, [Validators.required, Validators.min(0)]],
      cost_price: [0, [Validators.required, Validators.min(0)]],
      sku: ['', Validators.required],
      stock_quantity: [0, [Validators.required, Validators.min(0)]],
      min_stock_level: [0, Validators.required],
      category_id: [null, Validators.required],
      manufacturer: [''],
      material: [''],
      scale: [''],
      is_3d_print: [false],
      print_time_hours: [0],
      resin_type: [''],
      image_urls: [''],
      is_active: [true]
    });
  }

  ngOnInit(): void {
    this.loadCategories();
    if (this.isEditMode && this.data.product) {
      this.productForm.patchValue({
        name: this.data.product.name,
        description: this.data.product.description || '',
        price: this.data.product.price,
        cost_price: this.data.product.cost_price,
        sku: this.data.product.sku,
        stock_quantity: this.data.product.stock_quantity,
        min_stock_level: this.data.product.min_stock_level,
        category_id: this.data.product.category_id,
        manufacturer: this.data.product.manufacturer || '',
        material: this.data.product.material || '',
        scale: this.data.product.scale || '',
        is_3d_print: this.data.product.is_3d_print,
        print_time_hours: this.data.product.print_time_hours || 0,
        resin_type: this.data.product.resin_type || '',
        image_urls: this.data.product.image_urls ? this.data.product.image_urls.join(', ') : '',
        is_active: this.data.product.is_active
      });
    }
  }

  loadCategories(): void {
    this.productService.getCategories().subscribe(categories => {
      this.categories = categories;
    });
  }

  onSubmit(): void {
    if (this.productForm.invalid) {
      return;
    }

    const productData = {
      ...this.productForm.value,
      image_urls: this.productForm.value.image_urls
        ? this.productForm.value.image_urls.split(',').map((url: string) => url.trim())
        : []
    };

    this.dialogRef.close(productData);
  }

  onCancel(): void {
    this.dialogRef.close();
  }
}
