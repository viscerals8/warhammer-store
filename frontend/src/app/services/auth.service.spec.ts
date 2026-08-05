import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';

import { AuthService } from './auth.service';
import { environment } from '../../environments/environment';

function fakeJwt(payload: object): string {
  const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
  const body = btoa(JSON.stringify(payload));
  return `${header}.${body}.fake-signature`;
}

describe('AuthService', () => {
  let service: AuthService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    localStorage.clear();
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [AuthService]
    });
    service = TestBed.inject(AuthService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
    localStorage.clear();
  });

  it('is not logged in and not admin with a clean localStorage', () => {
    expect(service.isLoggedIn()).toBeFalse();
    expect(service.isAdmin()).toBeFalse();
  });

  it('login() stores the token and decodes is_admin from the JWT payload', () => {
    const token = fakeJwt({ sub: 'admin@warhammer.store', user_id: 7, is_admin: true });

    service.login('admin@warhammer.store', 'admin123').subscribe();

    const req = httpMock.expectOne(`${environment.apiUrl}/auth/login`);
    expect(req.request.method).toBe('POST');
    req.flush({ access_token: token, token_type: 'bearer' });

    expect(service.getToken()).toBe(token);
    expect(service.isLoggedIn()).toBeTrue();
    expect(service.isAdmin()).toBeTrue();
    expect(service.currentUserValue?.email).toBe('admin@warhammer.store');
    expect(service.currentUserValue?.id).toBe(7);
  });

  it('login() with a non-admin user does not grant admin access', () => {
    const token = fakeJwt({ sub: 'customer@example.com', user_id: 3, is_admin: false });

    service.login('customer@example.com', 'pw').subscribe();

    const req = httpMock.expectOne(`${environment.apiUrl}/auth/login`);
    req.flush({ access_token: token, token_type: 'bearer' });

    expect(service.isLoggedIn()).toBeTrue();
    expect(service.isAdmin()).toBeFalse();
  });

  it('logout() clears the token and current user', () => {
    const token = fakeJwt({ sub: 'admin@warhammer.store', user_id: 1, is_admin: true });
    service.login('admin@warhammer.store', 'admin123').subscribe();
    httpMock.expectOne(`${environment.apiUrl}/auth/login`).flush({ access_token: token });

    service.logout();

    expect(service.isLoggedIn()).toBeFalse();
    expect(service.currentUserValue).toBeNull();
  });

  it('register() posts the new user to the register endpoint', () => {
    const payload = { email: 'new@example.com', password: 'pw', full_name: 'New User' };

    service.register(payload).subscribe();

    const req = httpMock.expectOne(`${environment.apiUrl}/auth/register`);
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual(payload);
    req.flush({ id: 1, email: payload.email, is_admin: false });
  });
});
