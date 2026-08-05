import { Component, OnInit } from '@angular/core';
import { DashboardService } from '../../services/dashboard.service';
import { AuthService } from '../../services/auth.service';
import { DashboardStats, TopSellingProduct, MonthlySale } from '../../models/interface.model';
import { Router } from '@angular/router';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  stats!: DashboardStats;
  topProducts: TopSellingProduct[] = [];
  monthlySales: MonthlySale[] = [];
  loading = false;
  isAdmin = false;

  constructor(
    private dashboardService: DashboardService,
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.isAdmin = this.authService.isAdmin();
    if (!this.isAdmin) {
      this.router.navigate(['/home']);
      return;
    }
    this.loadDashboard();
  }

  loadDashboard(): void {
    this.loading = true;
    this.dashboardService.getStats().subscribe({
      next: (stats) => {
        this.stats = stats;
        this.loading = false;
      },
      error: (err) => {
        console.error('Failed to load dashboard stats', err);
        this.loading = false;
      }
    });

    this.dashboardService.getTopSellingProducts().subscribe({
      next: (products) => {
        this.topProducts = products;
      },
      error: (err) => {
        console.error('Failed to load top products', err);
      }
    });

    this.dashboardService.getMonthlySales().subscribe({
      next: (sales) => {
        this.monthlySales = sales;
      },
      error: (err) => {
        console.error('Failed to load monthly sales', err);
      }
    });
  }
}
