import { Component, OnInit } from '@angular/core';
import { RouterOutlet, Router } from '@angular/router';
import { AuthService, User } from '../services/auth.service';
import { CommonModule } from '@angular/common';
import Swal from 'sweetalert2';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterOutlet],
  styleUrls: ['./dashboard.component.scss'],
  template: `
    <div class="min-h-screen bg-gray-100 dashboard-admin">
      <!-- Mobile Menu Button -->
      <div class="lg:hidden fixed bottom-4 right-4 z-50">
        <button 
          (click)="toggleMobileMenu()"
          class="bg-emerald-600 text-white p-3 rounded-full shadow-lg hover:bg-emerald-700 transition-colors"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16m-7 6h7" />
          </svg>
        </button>
      </div>

      <!-- Mobile Menu -->
      <div *ngIf="showMobileMenu" class="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-40">
        <div class="bg-white w-64 h-full absolute right-0 shadow-xl p-4">
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-lg font-semibold">Menu</h2>
            <button (click)="toggleMobileMenu()" class="text-gray-500">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <div class="space-y-4">
            <button 
              (click)="navigateToStats(); toggleMobileMenu()"
              class="w-full text-left px-4 py-2 rounded hover:bg-emerald-50 transition-colors flex items-center space-x-2"
              [class.bg-emerald-50]="currentPage === 'stats'"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              <span>{{ currentUser?.title }}</span>
            </button>
            <button 
              (click)="navigateToPowerBI(); toggleMobileMenu()"
              class="w-full text-left px-4 py-2 rounded hover:bg-emerald-50 transition-colors flex items-center space-x-2"
              [class.bg-emerald-50]="currentPage === 'powerbi'"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
              </svg>
              <span>Power BI</span>
            </button>
            <button 
              (click)="toggleProfile(); toggleMobileMenu()"
              class="w-full text-left px-4 py-2 rounded hover:bg-emerald-50 transition-colors flex items-center space-x-2"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              <span>Profile</span>
            </button>
            <button 
              (click)="confirmLogout()"
              class="w-full text-left px-4 py-2 rounded hover:bg-emerald-50 transition-colors flex items-center space-x-2"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              <span>Logout</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Top Navigation Bar -->
      <nav class="bg-emerald-600 text-white p-4 shadow-lg">
        <div class="container mx-auto">
          <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
            <div class="flex items-center space-x-4">
              <img 
                src="assets/logo.png" 
                alt="Logo" 
                class="h-10 w-auto"
              />
              <div class="flex items-center space-x-3">
              
                <div>
                  <h1 class="text-xl font-bold">{{ currentUser?.name }}</h1>
                  <p class="text-sm text-emerald-200">{{ currentUser?.title }}</p>
                </div>
              </div>
            </div>
            <div class="hidden lg:flex items-center space-x-4">
              <button 
                (click)="navigateToStats()" 
                class="px-4 py-2 bg-emerald-700 rounded hover:bg-emerald-800 transition-colors flex items-center space-x-2"
                [class.bg-emerald-800]="currentPage === 'stats'"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                <span>{{ currentUser?.title }}</span>
              </button>
              <button 
                (click)="navigateToPowerBI()" 
                class="px-4 py-2 bg-emerald-700 rounded hover:bg-emerald-800 transition-colors flex items-center space-x-2"
                [class.bg-emerald-800]="currentPage === 'powerbi'"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                </svg>
                <span>Power BI</span>
              </button>
              <button 
                (click)="toggleProfile()"
                class="px-4 py-2 bg-emerald-700 rounded hover:bg-emerald-800 transition-colors flex items-center space-x-2"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                <span>Profile</span>
              </button>
              <button 
                (click)="confirmLogout()" 
                class="px-4 py-2 bg-emerald-700 rounded hover:bg-emerald-800 transition-colors flex items-center space-x-2"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
                <span>Logout</span>
              </button>
            </div>
          </div>
        </div>
      </nav>

      <!-- Main Content -->
      <main class="container mx-auto p-4 lg:p-6">
       <!-- Profile Modal -->
      <div *ngIf="showProfile" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div class="bg-white rounded-2xl shadow-2xl w-full max-w-lg transform transition-all duration-300 scale-100 overflow-hidden max-h-[90vh]">
          <!-- Modal Header -->
          <div class="p-6 bg-gradient-to-r from-emerald-600 to-green-600 rounded-t-2xl relative">
            <button 
              (click)="toggleProfile()" 
              class="absolute top-6 right-6 text-white/80 hover:text-white transition-colors"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
            
            <!-- Avatar Section -->
            <div class="flex items-center justify-center mt-4">
              <div class="w-24 h-24 bg-white rounded-full flex items-center justify-center shadow-lg">
                <span class="text-4xl font-bold text-emerald-600">{{ getUserInitials() }}</span>
              </div>
            </div>

            <!-- Name as Title -->
            <div class="text-center mt-4">
              <h2 class="text-2xl font-bold text-white">{{ currentUser?.name }}</h2>
            </div>
          </div>

          <!-- Modal Content -->
          <div class="p-6 space-y-6 overflow-y-auto max-h-[calc(90vh-100px)]">
            <!-- User Info -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          
              <div class="space-y-2 md:col-span-2">
                <label class="text-sm font-medium text-gray-500">Title</label>
                <p class="text-lg font-semibold text-gray-900">{{ currentUser?.title }}</p>
              </div>
              <div class="space-y-2 md:col-span-2">
                <label class="text-sm font-medium text-gray-500">Email</label>
                <p class="text-lg font-semibold text-gray-900">{{ currentUser?.email }}</p>
              </div>
            </div>

            <!-- Responsibilities -->
            <div class="space-y-3">
              <h3 class="text-lg font-semibold text-gray-900">Responsibilities</h3>
              <div class="bg-gray-50 rounded-xl p-4">
                <ul class="space-y-2">
                  <li *ngFor="let responsibility of currentUser?.responsibilities" 
                      class="flex items-center text-gray-700">
                    <span class="w-2 h-2 bg-emerald-500 rounded-full mr-3"></span>
                    {{ responsibility }}
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>


        <!-- Dashboard Content -->
        <router-outlet></router-outlet>
      </main>
    </div>
  `
})
export class DashboardComponent implements OnInit {
  currentUser: User | null = null;
  showProfile: boolean = false;
  showMobileMenu: boolean = false;
  currentPage: 'stats' | 'powerbi' = 'stats';

  constructor(
    private authService: AuthService,
    private router: Router
  ) {
    this.authService.currentUser$.subscribe(user => {
      this.currentUser = user;
    });
  }

  ngOnInit() {
    this.currentUser = this.authService.getCurrentUser();
  }

  getUserInitials(): string {
    if (!this.currentUser?.name) return '';
    return this.currentUser.name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase();
  }

  toggleProfile() {
    this.showProfile = !this.showProfile;
  }

  toggleMobileMenu() {
    this.showMobileMenu = !this.showMobileMenu;
  }

  navigateToStats() {
    this.currentPage = 'stats';
    this.router.navigate(['/dashboard', this.currentUser?.role]);
  }

  navigateToPowerBI() {
    this.currentPage = 'powerbi';
    this.router.navigate(['/dashboard', this.currentUser?.role, 'powerbi']);
  }

  async confirmLogout() {
    const result = await Swal.fire({
      title: 'Confirm Logout',
      text: 'Are you sure you want to log out?',
      icon: 'question',
      showCancelButton: true,
      confirmButtonText: 'Yes, log me out',
      cancelButtonText: 'Cancel',
      confirmButtonColor: '#059669',
      cancelButtonColor: '#6B7280',
      customClass: {
        popup: 'rounded-lg',
        confirmButton: 'rounded-md',
        cancelButton: 'rounded-md'
      }
    });

    if (result.isConfirmed) {
      this.logout();
    }
  }

  private logout() {
    this.authService.logout();
  }
}