import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { ProductService } from '../../services/product.service';
import { Product } from '../../models/interface.model';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit {
  featuredProducts: Product[] = [];
  loading = true;
  testimonials = [
    {
      text: "Amazing quality miniatures! The Space Marines I ordered are incredibly detailed and the paint job is perfect.",
      author: "Alex M."
    },
    {
      text: "Best Warhammer store online. Fast shipping and excellent customer service.",
      author: "Sarah K."
    },
    {
      text: "The 3D printed terrain is fantastic. Great detail and perfect for my gaming table.",
      author: "Mike R."
    }
  ];

  constructor(
    private productService: ProductService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadFeaturedProducts();
  }

  loadFeaturedProducts(): void {
    this.productService.getProducts({ limit: 8, is_active: true }).subscribe({
      next: (products) => {
        this.featuredProducts = products;
        this.loading = false;
      },
      error: (err) => {
        console.error('Failed to load products', err);
        this.loading = false;
      }
    });
  }

  viewProduct(id: number): void {
    this.router.navigate(['/products', id]);
  }

  viewAllProducts(): void {
    this.router.navigate(['/products']);
  }
}
