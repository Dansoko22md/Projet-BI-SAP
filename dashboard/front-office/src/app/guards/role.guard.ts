import { Injectable } from '@angular/core';
import { ActivatedRouteSnapshot, CanActivate, Router, UrlTree } from '@angular/router';
import { UserSessionService } from '../services/user-session.service';

@Injectable({
  providedIn: 'root'
})
export class RoleGuard implements CanActivate {
  constructor(
    private userSessionService: UserSessionService,
    private router: Router
  ) {}

  canActivate(route: ActivatedRouteSnapshot): boolean | UrlTree {
    const user = this.userSessionService.getCurrentUser();
    const requiredRole = route.data['role'];

    console.log('[RoleGuard] User:', user);
    console.log('[RoleGuard] Required role:', requiredRole);

    if (!user) {
      console.log('[RoleGuard] Access denied: user not authenticated');
      return this.router.createUrlTree(['/login']);
    }

    if (user.role === requiredRole) {
      console.log('[RoleGuard] Access granted');
      return true;
    }

    console.log('[RoleGuard] Access denied: role mismatch');
    return this.router.createUrlTree(['/dashboard', user.role]);
  }
}
