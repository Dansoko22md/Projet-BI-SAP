import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { CommonModule } from '@angular/common';
import { trigger, state, style, transition, animate } from '@angular/animations';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss'],
  standalone: true,
  imports: [FormsModule, CommonModule],
  animations: [
    trigger('loadingState', [
      state('inactive', style({
        opacity: 0,
        transform: 'scale(0.9)'
      })),
      state('active', style({
        opacity: 1,
        transform: 'scale(1)'
      })),
      transition('inactive => active', animate('300ms ease-in')),
      transition('active => inactive', animate('200ms ease-out'))
    ])
  ]
})
export class LoginComponent {
  email = '';
  password = '';
  loading = false;
  error = '';
  loadingState = 'inactive';
  loadingProgress = 0;
  loadingInterval: any;

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  onSubmit(): void {
    if (!this.email || !this.password) {
      this.error = 'Veuillez remplir tous les champs';
      this.shakeForm();
      return;
    }

    this.loading = true;
    this.error = '';
    this.loadingState = 'active';
    this.startLoadingAnimation();

    this.authService.login(this.email, this.password).subscribe({
      next: (success) => {
        this.completeLoadingAnimation(() => {
          this.loading = false;
          if (success) {
            const user = this.authService.getCurrentUser();
            if (user) {
              this.router.navigate(['/dashboard', user.role]);
            }
          } else {
            this.loadingState = 'inactive';
            this.error = 'Email ou mot de passe incorrect';
            this.shakeForm();
          }
        });
      },
      error: () => {
        this.stopLoadingAnimation();
        this.loading = false;
        this.loadingState = 'inactive';
        this.error = 'Une erreur est survenue, veuillez réessayer.';
        this.shakeForm();
      }
    });
  }

  startLoadingAnimation(): void {
    this.loadingProgress = 0;
    this.loadingInterval = setInterval(() => {
      if (this.loadingProgress < 80) {
        this.loadingProgress += Math.random() * 10;
        if (this.loadingProgress > 80) {
          this.loadingProgress = 80;
        }
      }
    }, 200);
  }

  completeLoadingAnimation(callback: () => void): void {
    clearInterval(this.loadingInterval);
    this.loadingProgress = 100;
    setTimeout(callback, 500);
  }

  stopLoadingAnimation(): void {
    clearInterval(this.loadingInterval);
    this.loadingProgress = 0;
  }

  shakeForm(): void {
    const form = document.querySelector('form');
    if (form) {
      form.classList.add('shake-animation');
      setTimeout(() => {
        form.classList.remove('shake-animation');
      }, 500);
    }
  }
}