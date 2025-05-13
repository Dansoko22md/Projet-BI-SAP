import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { KpiCardComponent } from '../shared/kpi-card.component';
import { PredictionFormComponent } from '../shared/prediction-form.component';

@Component({
  selector: 'app-maintenance',
  standalone: true,
  imports: [CommonModule, KpiCardComponent, PredictionFormComponent],
  template: `
    <div class="space-y-6">
      <div class="bg-white rounded-lg shadow-md p-6">
        <h2 class="text-2xl font-bold text-gray-800 mb-4">Directeur Maintenance</h2>
        <p class="text-gray-600 mb-2">Tableau de bord pour la gestion de la maintenance et des équipements</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <app-kpi-card
          title="Disponibilité"
          value="94.5%"
          description="Taux de disponibilité des équipements"
        ></app-kpi-card>
        <app-kpi-card
          title="Maintenance Préventive"
          value="78%"
          description="Taux de réalisation du planning préventif"
        ></app-kpi-card>
        <app-kpi-card
          title="Efficacité Énergétique"
          value="89%"
          description="Performance énergétique des installations"
        ></app-kpi-card>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <app-prediction-form
          title="Prédictions Maintenance"
          [predictionTypes]="[
            {
              id: 'pannes',
              label: 'Prédiction des Pannes',
              fields: [
                { id: 'age', label: 'Age de l\\'équipement (années)', type: 'number', placeholder: '5', min: 0, step: 0.5 },
                { id: 'utilisation', label: 'Taux d\\'utilisation (%)', type: 'number', placeholder: '80', min: 0, max: 100 },
                { id: 'temperature', label: 'Température moyenne (°C)', type: 'number', placeholder: '25', min: -50, max: 100 }
              ]
            },
            {
              id: 'energie',
              label: 'Prédiction Consommation Énergétique',
              fields: [
                { id: 'puissance', label: 'Puissance nominale (kW)', type: 'number', placeholder: '100', min: 0 },
                { id: 'duree', label: 'Durée d\\'utilisation (h/jour)', type: 'number', placeholder: '16', min: 0, max: 24 },
                { id: 'charge', label: 'Charge moyenne (%)', type: 'number', placeholder: '75', min: 0, max: 100 }
              ]
            },
            {
              id: 'maintenance',
              label: 'Planification Maintenance Préventive',
              fields: [
                { id: 'cycles', label: 'Cycles d\\'opération', type: 'number', placeholder: '1000', min: 0 },
                { id: 'usure', label: 'Niveau d\\'usure (%)', type: 'number', placeholder: '45', min: 0, max: 100 },
                { id: 'vibration', label: 'Niveau de vibration (mm/s)', type: 'number', placeholder: '2.5', min: 0, step: 0.1 }
              ]
            }
          ]"
        ></app-prediction-form>

        <div class="bg-white rounded-lg shadow-md p-6">
        <h3 class="text-xl font-semibold mb-4">Sustainable Development Goals</h3>
        <div class="grid grid-cols-1 gap-4">
          <div class="sdg-card flex items-center p-3 border rounded-lg border-emerald-200 bg-emerald-50 hover:shadow-md transition-shadow">
            <div class="flex-shrink-0 mr-4">
              <img [src]="sdgImages.sdg12" alt="SDG 12" class="w-16 h-16 rounded-md">
            </div>
            <div>
              <h4 class="font-medium text-emerald-800">SDG 12</h4>
              <p class="text-gray-700">Responsible Consumption and Production</p>
              <div class="mt-1 h-1 w-full bg-gray-200 rounded-full overflow-hidden">
                <div class="bg-emerald-500 h-full rounded-full" [style.width]="sdgProgress.sdg12"></div>
              </div>
            </div>
          </div>
          
          <div class="sdg-card flex items-center p-3 border rounded-lg border-blue-200 bg-blue-50 hover:shadow-md transition-shadow">
            <div class="flex-shrink-0 mr-4">
              <img [src]="sdgImages.sdg16" alt="SDG 16" class="w-16 h-16 rounded-md">
            </div>
            <div>
              <h4 class="font-medium text-blue-800">SDG 16</h4>
              <p class="text-gray-700">Promote peaceful and inclusive societies for all.</p>
              <div class="mt-1 h-1 w-full bg-gray-200 rounded-full overflow-hidden">
                <div class="bg-blue-500 h-full rounded-full" [style.width]="sdgProgress.sdg16"></div>
              </div>
            </div>
          </div>
          
          <div class="sdg-card flex items-center p-3 border rounded-lg border-orange-200 bg-orange-50 hover:shadow-md transition-shadow">
            <div class="flex-shrink-0 mr-4">
              <img [src]="sdgImages.sdg7" alt="SDG 7" class="w-16 h-16 rounded-md">
            </div>
            <div>
              <h4 class="font-medium text-orange-800">SDG 7</h4>
              <p class="text-gray-700">Affordable and Clean Energy </p>
              <div class="mt-1 h-1 w-full bg-gray-200 rounded-full overflow-hidden">
                <div class="bg-orange-500 h-full rounded-full" [style.width]="sdgProgress.sdg7"></div>
              </div>
            </div>
          </div>

          <button 
            (click)="refreshSdgProgress()" 
            class="mt-2 flex items-center justify-center py-2 px-4 bg-emerald-600 text-white rounded-md hover:bg-emerald-700 transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh Goals
          </button>
        </div>
      
      </div>
    </div>
  `
})
export class MaintenanceComponent {
   // SDG images URLs
sdgImages = {
  sdg12: 'https://www.unoosa.org/images/ourwork/SDGs/E_SDG_goals_icons-individual-rgb-12.png',
  sdg16: 'https://tse3.mm.bing.net/th/id/OIP.iO0u1hr11W44JElgdKi7CQAAAA?cb=iwc1&w=446&h=440&rs=1&pid=ImgDetMain',
  sdg7: 'https://th.bing.com/th/id/R.4fc8378eeb9d009248b019e3506945b5?rik=F%2beZoC5vje5j4A&pid=ImgRaw&r=0'
};
  // Progress for SDG progress bars
  sdgProgress = {
    sdg12: '65%',
    sdg16: '45%',
    sdg7: '80%'
  };
  refreshSdgProgress() {
    this.sdgProgress = {
      sdg12: `${Math.round(50 + Math.random() * 40)}%`,
      sdg16: `${Math.round(40 + Math.random() * 35)}%`,
      sdg7: `${Math.round(60 + Math.random() * 30)}%`
    };
  }
}