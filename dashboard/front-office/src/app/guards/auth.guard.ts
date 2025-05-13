import { Injectable } from '@angular/core';
import { CanActivate, Router, UrlTree } from '@angular/router';
import { UserSessionService } from '../services/user-session.service';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {
  constructor(
    private userSessionService: UserSessionService,
    private router: Router
  ) {}

  canActivate(): boolean | UrlTree {
    const isAuthenticated = this.userSessionService.isAuthenticated();
    
    if (isAuthenticated) {
      return true;
    }

    // Redirection sécurisée vers /login si non authentifié
    return this.router.createUrlTree(['/login']);
  }
}
