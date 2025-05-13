import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-kpi-card',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden group">
      <div class="relative">
        <!-- Gradient Overlay -->
        <div class="absolute inset-0 bg-gradient-to-br from-emerald-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
        
        <!-- Card Content -->
        <div class="p-6">
          <!-- Header -->
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-lg font-semibold text-gray-800 group-hover:text-emerald-600 transition-colors duration-300">
              {{ title }}
            </h3>
            <div class="relative">
              <div class="w-10 h-10 rounded-full bg-emerald-50 flex items-center justify-center group-hover:bg-emerald-100 transition-colors duration-300">
                <svg class="w-5 h-5 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
                </svg>
              </div>
              <!-- Pulse Effect -->
              <div *ngIf="isUpdating" class="absolute inset-0 rounded-full">
                <div class="absolute inset-0 animate-ping rounded-full bg-emerald-400 opacity-75"></div>
              </div>
            </div>
          </div>

          <!-- Value -->
          <div class="mb-4">
            <div class="flex items-baseline">
              <span class="text-4xl font-bold text-gray-900 transition-all duration-500 transform"
                    [class.scale-110]="isUpdating">
                {{ displayValue }}
              </span>
              <span class="ml-2 text-sm font-medium text-gray-500">vs précédent</span>
            </div>
            <!-- Progress Bar -->
            <div class="mt-3 relative h-2 bg-gray-100 rounded-full overflow-hidden">
              <div class="absolute left-0 top-0 h-full bg-emerald-500 rounded-full transition-all duration-500"
                   [style.width]="displayValue"></div>
            </div>
          </div>

          <!-- Description -->
          <p class="text-sm text-gray-600 group-hover:text-gray-700 transition-colors duration-300">
            {{ description }}
          </p>

          <!-- Trend Indicator -->
          <div class="mt-4 flex items-center space-x-2">
            <div class="flex items-center text-emerald-500">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
              </svg>
              <span class="ml-1 text-sm font-medium">+12%</span>
            </div>
            <span class="text-sm text-gray-500">depuis le dernier mois</span>
          </div>
        </div>

        <!-- Bottom Border Gradient -->
        <div class="h-1 bg-gradient-to-r from-emerald-400 to-green-400 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></div>
      </div>
    </div>
  `
})
export class KpiCardComponent implements OnChanges {
  @Input() title: string = '';
  @Input() value: string = '';
  @Input() description: string = '';
  @Input() isUpdating: boolean = false;

  displayValue: string = '';
  private animationFrame: number | null = null;

  ngOnChanges(changes: SimpleChanges) {
    if (changes['value'] && changes['value'].currentValue !== changes['value'].previousValue) {
      this.animateValue(changes['value'].previousValue, changes['value'].currentValue);
    }
  }

  private animateValue(start: string, end: string) {
    if (this.animationFrame) {
      cancelAnimationFrame(this.animationFrame);
    }

    const startNum = parseInt(start || '0');
    const endNum = parseInt(end || '0');
    const duration = 1000;
    const startTime = performance.now();

    const updateValue = (currentTime: number) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);

      const easeOutQuart = 1 - Math.pow(1 - progress, 4);
      
      const current = Math.round(startNum + (endNum - startNum) * easeOutQuart);
      this.displayValue = `${current}%`;

      if (progress < 1) {
        this.animationFrame = requestAnimationFrame(updateValue);
      } else {
        this.displayValue = end;
        this.animationFrame = null;
      }
    };

    this.animationFrame = requestAnimationFrame(updateValue);
  }

  ngOnDestroy() {
    if (this.animationFrame) {
      cancelAnimationFrame(this.animationFrame);
    }
  }
}