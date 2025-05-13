import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { User } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class UserSessionService {
  private readonly USER_KEY = 'currentUser';
  private currentUserSubject = new BehaviorSubject<User | null>(this.getStoredUser());

  constructor() {}

  private getStoredUser(): User | null {
    const storedUser = localStorage.getItem(this.USER_KEY);
    return storedUser ? JSON.parse(storedUser) : null;
  }

  setCurrentUser(user: User | null): void {
    if (user) {
      localStorage.setItem(this.USER_KEY, JSON.stringify(user));
    } else {
      localStorage.removeItem(this.USER_KEY);
    }
    this.currentUserSubject.next(user);
  }

  getCurrentUser(): User | null {
    return this.currentUserSubject.value;
  }

  getCurrentUser$(): Observable<User | null> {
    return this.currentUserSubject.asObservable();
  }

  isAuthenticated(): boolean {
    return !!this.getCurrentUser();
  }

  clearSession(): void {
    localStorage.removeItem(this.USER_KEY);
    this.currentUserSubject.next(null);
  }
}