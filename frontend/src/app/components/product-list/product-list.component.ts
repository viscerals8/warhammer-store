import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { ProductService } from '../../services/product.service';
import { CartService } from '../../services/cart.service';
import { Product, Category } from '../../models/interface.model';
import { warhammerPlaceholders } from '../../utils/warhammer-images';

@Component({
  selector: 'app-product-list',
  templateUrl: './product-list.component.html',
  styleUrls: ['./product-list.component.css']
})
export class ProductListComponent implements OnInit {
  products: Product[] = [];
  categories: Category[] = [];
  loading = false;
  selectedCategory: number | null = null;
  searchTerm = '';
  currentPage = 0;
  pageSize = 12;
  totalProducts = 0;

  constructor(
    private productService: ProductService,
    private cartService: CartService,
    private router: Router,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    this.loadCategories();
    this.loadProducts();

    this.route.queryParams.subscribe(params => {
      if (params['category']) {
        this.selectedCategory = +params['category'];
      }
      if (params['search']) {
        this.searchTerm = params['search'];
      }
      this.loadProducts();
    });
  }

  getImageForProduct(product: Product): string {
    if (product.image_urls && product.image_urls.length > 0) {
      return product.image_urls[0];
    }
    // Return a deterministic warhammer image based on product id
    const index = product.id % warhammerPlaceholders.length;
    return warhammerPlaceholders[index];
  }

  loadCategories(): void {
    this.productService.getCategories().subscribe(categories => {
      this.categories = categories;
    });
  }

  loadProducts(): void {
    this.loading = true;
    const params: any = {
      skip: this.currentPage * this.pageSize,
      limit: this.pageSize,
      is_active: true
    };
    if (this.selectedCategory) {
      params.category_id = this.selectedCategory;
    }
    if (this.searchTerm) {
      params.search = this.searchTerm;
    }

    this.productService.getProducts(params).subscribe({
      next: (products) => {
        this.products = products;
        this.totalProducts = products.length;
        this.loading = false;
      },
      error: (err) => {
        console.error('Failed to load products', err);
        this.loading = false;
      }
    });
  }

  onCategoryFilter(categoryId: number | null): void {
    this.selectedCategory = categoryId;
    this.currentPage = 0;
    this.updateUrlAndReload();
  }

  onSearch(): void {
    this.currentPage = 0;
    this.updateUrlAndReload();
  }

  onPageChange(event: any): void {
    this.currentPage = event.pageIndex;
    this.loadProducts();
  }

  private updateUrlAndReload(): void {
    const queryParams: any = {};
    if (this.selectedCategory) {
      queryParams.category = this.selectedCategory;
    }
    if (this.searchTerm) {
      queryParams.search = this.searchTerm;
    }
    this.router.navigate([], { relativeTo: this.route, queryParams, queryParamsHandling: 'merge' });
    this.loadProducts();
  }

  viewProduct(id: number): void {
    this.router.navigate(['/products', id]);
  }

  addToCart(product: Product): void {
    this.cartService.addToCart(product.id, 1).subscribe({
      next: () => {
        this.updateCartCount();
      },
      error: (err) => {
        console.error('Failed to add to cart', err);
      }
    });
  }

  private updateCartCount(): void {
    this.cartService.getCart().subscribe();
  }
}
