import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  template: `
    <app-navbar></app-navbar>
    <main class="main-content">
      <div class="container">
        <router-outlet></router-outlet>
      </div>
    </main>
    <footer class="footer">
      <div class="container footer-content">
        <div class="footer-section">
          <h3>WARHAMMER STORE</h3>
          <p>Your premier destination for Warhammer miniatures and custom 3D prints</p>
        </div>
        <div class="footer-section">
          <h4>Quick Links</h4>
          <a routerLink="/home">Home</a>
          <a routerLink="/products">Products</a>
          <a routerLink="/cart">Cart</a>
        </div>
        <div class="footer-section newsletter">
          <h4>Newsletter</h4>
          <p>Subscribe for updates and promotions</p>
          <div class="newsletter-form">
            <input type="email" placeholder="Your email" [(ngModel)]="email">
            <button mat-raised-button color="primary">Subscribe</button>
          </div>
        </div>
      </div>
      <div class="footer-bottom">
        <p>&copy; 2024 Warhammer Store. All rights reserved.</p>
      </div>
    </footer>
  `,
  styles: [`
    .main-content {
      min-height: calc(100vh - 64px);
      padding-top: 24px;
      padding-bottom: 48px;
    }
    
    .footer {
      background: rgba(26, 26, 46, 0.95);
      border-top: 1px solid var(--gold-color);
      padding: 32px 0 0;
      backdrop-filter: blur(10px);
    }
    
    .footer-content {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 24px;
      margin-bottom: 24px;
    }
    
    .footer-section h3, .footer-section h4 {
      color: var(--gold-color);
      margin-top: 0;
    }
    
    .footer-section p {
      color: var(--text-secondary);
    }
    
    .footer-section a {
      display: block;
      color: var(--text-primary);
      text-decoration: none;
      margin: 8px 0;
      transition: color 0.2s;
    }
    
    .footer-section a:hover {
      color: var(--gold-color);
    }
    
    .newsletter-form {
      display: flex;
      gap: 8px;
      margin-top: 8px;
    }
    
    .newsletter-form input {
      flex: 1;
      padding: 8px;
      border: 1px solid var(--gold-color);
      border-radius: 4px;
      background: rgba(26, 26, 46, 0.5);
      color: var(--text-primary);
    }
    
    .newsletter-form input::placeholder {
      color: var(--text-secondary);
    }
    
    .footer-bottom {
      text-align: center;
      padding: 16px;
      border-top: 1px solid rgba(212, 175, 55, 0.3);
      color: var(--text-secondary);
    }
  `]
})
export class AppComponent {
  email = '';
}
