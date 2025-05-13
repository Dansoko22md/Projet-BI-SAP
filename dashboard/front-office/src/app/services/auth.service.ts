import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { UserSessionService } from './user-session.service';
import { Router } from '@angular/router';
export interface User {
  id: string;
  role: 'achats' | 'developpement' | 'maintenance' | 'qualite' | 'admin';
  name: string;
  email: string;
  title: string;
  responsibilities: string[];
  kpis: string[];
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();

  private readonly users: { [key: string]: User } = {
    'procurement@ecovision.com': { 
      id: '1', 
      role: 'achats', 
      name: 'Procurement Director',
      email: 'procurement@ecovision.com',
      title: 'Procurement and Production Director',
      responsibilities: [
        'Supply chain management',
        'Purchase cost optimization',
        'Production planning',
        'Inventory management',
        'Supplier relations'
      ],
      kpis: [
        'Stock Level',
        'Production Efficiency',
        'Sustainable Suppliers'
      ]
    },
    'sustainability@ecovision.com': { 
      id: '2', 
      role: 'developpement', 
      name: 'Sustainability Manager',
      email: 'sustainability@ecovision.com',
      title: 'Sustainability Manager',
      responsibilities: [
        'Environmental strategy',
        'Carbon footprint reduction',
        'Renewable energy management',
        'Environmental certification',
        'CSR reporting'
      ],
      kpis: [
        'CO2 Reduction',
        'Renewable Energy',
        'Recycling'
      ]
    },
    'maintenance@ecovision.com': { 
      id: '3', 
      role: 'maintenance', 
      name: 'Maintenance Director',
      email: 'maintenance@ecovision.com',
      title: 'Maintenance Director',
      responsibilities: [
        'Preventive maintenance',
        'Equipment management',
        'Performance optimization',
        'Facility safety',
        'Intervention management'
      ],
      kpis: [
        'Availability',
        'Preventive Maintenance',
        'Energy Efficiency'
      ]
    },
    'quality@ecovision.com': { 
      id: '4', 
      role: 'qualite', 
      name: 'Quality Manager',
      email: 'quality@ecovision.com',
      title: 'Quality and Compliance Manager',
      responsibilities: [
        'Quality control',
        'Standards management',
        'Internal audits',
        'Product traceability',
        'Continuous improvement'
      ],
      kpis: [
        'Compliance',
        'Product Quality',
        'Traceability'
      ]
    },
    'admin@ecovision.com': {
      id: '5',
      role: 'admin',
      name: 'System Administrator',
      email: 'admin@ecovision.com',
      title: 'System Administrator',
      responsibilities: [
        'User access management',
        'Global supervision',
        'System configuration',
        'Platform maintenance',
        'Data security'
      ],
      kpis: [
        'System Availability',
        'Response Time',
        'Security'
      ]
    }
  };

  constructor(private userSessionService: UserSessionService,private router: Router) {
    const storedUser = this.userSessionService.getCurrentUser();
    if (storedUser) {
      this.currentUserSubject.next(storedUser);
    }
  }

  login(email: string, password: string): Observable<boolean> {
    return new Observable(subscriber => {
      setTimeout(() => {
        const user = this.users[email.toLowerCase()];
        if (user && password === 'Durable2025!') {
          this.currentUserSubject.next(user);
          this.userSessionService.setCurrentUser(user);
          subscriber.next(true);
        } else {
          subscriber.next(false);
        }
        subscriber.complete();
      }, 1000);
    });
  }


  logout(): void {
    this.currentUserSubject.next(null);
    this.userSessionService.clearSession();
    this.router.navigate(['/login']);
  }
  getCurrentUser(): User | null {
    return this.currentUserSubject.value;
  }
}