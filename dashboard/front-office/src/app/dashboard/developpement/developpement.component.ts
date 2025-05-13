import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { KpiCardComponent } from '../shared/kpi-card.component';
import { PredictionFormComponent } from '../shared/prediction-form.component';

@Component({
  selector: 'app-developpement',
  standalone: true,
  imports: [CommonModule, KpiCardComponent, PredictionFormComponent],
  template: `
    <div class="space-y-6">
      <div class="bg-white rounded-lg shadow-md p-6">
        <h2 class="text-2xl font-bold text-gray-800 mb-4">Responsable Développement Durable</h2>
        <p class="text-gray-600 mb-2">Tableau de bord pour la gestion de l'empreinte écologique</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <app-kpi-card
          title="Réduction CO2"
          value="-15%"
          description="Réduction des émissions depuis janvier"
        ></app-kpi-card>
        <app-kpi-card
          title="Énergie Renouvelable"
          value="45%"
          description="Part d'énergie renouvelable utilisée"
        ></app-kpi-card>
        <app-kpi-card
          title="Recyclage"
          value="82%"
          description="Taux de recyclage des déchets"
        ></app-kpi-card>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <app-prediction-form
          title="Prédictions Développement Durable"
          [predictionTypes]="[
            {
              id: 'carbone',
              label: 'Prédiction de l\\'Empreinte Carbone',
              fields: [
                { id: 'production', label: 'Volume de production (tonnes)', type: 'number', placeholder: '1000', min: 0 },
                { id: 'energie', label: 'Consommation énergétique (kWh)', type: 'number', placeholder: '50000', min: 0 },
                { id: 'transport', label: 'Distance transport (km)', type: 'number', placeholder: '5000', min: 0 }
              ]
            },
            {
              id: 'energie',
              label: 'Prédiction Énergies Renouvelables',
              fields: [
                { id: 'solaire', label: 'Production solaire (kWh)', type: 'number', placeholder: '10000', min: 0 },
                { id: 'eolien', label: 'Production éolienne (kWh)', type: 'number', placeholder: '15000', min: 0 },
                { id: 'biomasse', label: 'Production biomasse (kWh)', type: 'number', placeholder: '5000', min: 0 }
              ]
            },
            {
              id: 'dechets',
              label: 'Prédiction Gestion des Déchets',
              fields: [
                { id: 'volume', label: 'Volume total (tonnes)', type: 'number', placeholder: '100', min: 0 },
                { id: 'recyclable', label: 'Part recyclable (%)', type: 'number', placeholder: '75', min: 0, max: 100 },
                { id: 'valorisation', label: 'Taux valorisation (%)', type: 'number', placeholder: '85', min: 0, max: 100 }
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
              <img [src]="sdgImages.sdg13" alt="SDG 13" class="w-16 h-16 rounded-md">
            </div>
            <div>
            <h4 class="font-medium text-blue-800">SDG 13</h4>
              <p class="text-gray-700">Climate Action</p>
              <div class="mt-1 h-1 w-full bg-gray-200 rounded-full overflow-hidden">
                <div class="bg-blue-500 h-full rounded-full" [style.width]="sdgProgress.sdg13"></div>
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
    </div>
  `
})
export class DeveloppementComponent {
  // SDG images URLs
sdgImages = {
  sdg12: 'https://www.unoosa.org/images/ourwork/SDGs/E_SDG_goals_icons-individual-rgb-12.png',
  sdg13: 'https://tse4.mm.bing.net/th/id/OIP.Q1DGxFNLY1Zj6Hl73uvr2AHaEJ?cb=iwc1&rs=1&pid=ImgDetMain',
  sdg7: 'https://th.bing.com/th/id/R.4fc8378eeb9d009248b019e3506945b5?rik=F%2beZoC5vje5j4A&pid=ImgRaw&r=0'
};
  // Progress for SDG progress bars
  sdgProgress = {
    sdg12: '65%',
    sdg13: '45%',
    sdg7: '80%'
  };
  refreshSdgProgress() {
    this.sdgProgress = {
      sdg12: `${Math.round(50 + Math.random() * 40)}%`,
      sdg13: `${Math.round(40 + Math.random() * 35)}%`,
      sdg7: `${Math.round(60 + Math.random() * 30)}%`
    };
  }
}