import { Component, OnInit } from '@angular/core';
import { OrderService } from '../../services/order.service';

@Component({
  selector: 'app-orders',
  templateUrl: './orders.component.html',
  styleUrls: ['./orders.component.css']
})
export class OrdersComponent implements OnInit {
  orders: any[] = [];
  loading = true;
  displayedColumns: string[] = ['id', 'customer', 'total', 'status'];

  constructor(private orderService: OrderService) {}

  ngOnInit(): void {
    this.loadOrders();
  }

  loadOrders(): void {
    this.orderService.getAllOrders().subscribe({
      next: (orders) => {
        this.orders = orders;
        this.loading = false;
      }
    });
  }

  updateStatus(order: any): void {
    this.orderService.updateStatus(order.id, order.status).subscribe();
  }
}