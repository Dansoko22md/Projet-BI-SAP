import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { KpiCardComponent } from '../shared/kpi-card.component';
import { PredictionFormComponent } from '../shared/prediction-form.component';

@Component({
  selector: 'app-qualite',
  standalone: true,
  imports: [CommonModule, KpiCardComponent, PredictionFormComponent],
  template: `
    <div class="space-y-6">
      <div class="bg-white rounded-lg shadow-md p-6">
        <h2 class="text-2xl font-bold text-gray-800 mb-4">Responsable Qualité & Conformité</h2>
        <p class="text-gray-600 mb-2">Tableau de bord pour le suivi de la qualité et de la conformité</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <app-kpi-card
          title="Conformité"
          value="96%"
          description="Taux de conformité aux normes"
        ></app-kpi-card>
        <app-kpi-card
          title="Qualité Produits"
          value="99.2%"
          description="Taux de produits conformes"
        ></app-kpi-card>
        <app-kpi-card
          title="Traçabilité"
          value="100%"
          description="Taux de traçabilité des lots"
        ></app-kpi-card>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <app-prediction-form
          title="Prédictions Qualité"
          [predictionTypes]="[
            {
              id: 'qualite',
              label: 'Prédiction de la Qualité Produit',
              fields: [
                { id: 'temperature', label: 'Température du process (°C)', type: 'number', placeholder: '20', min: 0, max: 100 },
                { id: 'humidite', label: 'Humidité relative (%)', type: 'number', placeholder: '60', min: 0, max: 100 },
                { id: 'duree', label: 'Durée du process (heures)', type: 'number', placeholder: '2', min: 0, step: 0.5 }
              ]
            },
            {
              id: 'conformite',
              label: 'Prédiction de la Conformité',
              fields: [
                { id: 'parametres', label: 'Paramètres conformes (%)', type: 'number', placeholder: '95', min: 0, max: 100 },
                { id: 'controles', label: 'Contrôles réalisés (%)', type: 'number', placeholder: '90', min: 0, max: 100 },
                { id: 'incidents', label: 'Incidents qualité (nb/mois)', type: 'number', placeholder: '3', min: 0 }
              ]
            },
            {
              id: 'tracabilite',
              label: 'Analyse de la Traçabilité',
              fields: [
                { id: 'lots', label: 'Nombre de lots', type: 'number', placeholder: '100', min: 0 },
                { id: 'scanning', label: 'Taux de scanning (%)', type: 'number', placeholder: '98', min: 0, max: 100 },
                { id: 'precision', label: 'Précision données (%)', type: 'number', placeholder: '99.5', min: 0, max: 100, step: 0.1 }
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
              <img [src]="sdgImages.sdg16" alt="SDG 13" class="w-16 h-16 rounded-md">
            </div>
            <div>
              <h4 class="font-medium text-blue-800">SDG 16</h4>
              <p class="text-gray-700">Promote peaceful and inclusive societies for all.</p>
              <div class="mt-1 h-1 w-full bg-gray-200 rounded-full overflow-hidden">
                <div class="bg-blue-500 h-full rounded-full" [style.width]="sdgProgress.sdg13"></div>
              </div>
            </div>
          </div>
          
          <div class="sdg-card flex items-center p-3 border rounded-lg border-orange-200 bg-orange-50 hover:shadow-md transition-shadow">
            <div class="flex-shrink-0 mr-4">
              <img [src]="sdgImages.sdg9" alt="SDG 9" class="w-16 h-16 rounded-md">
            </div>
            <div>
              <h4 class="font-medium text-orange-800">SDG 9</h4>
              <p class="text-gray-700">Industry, Innovation, and Infrastructure</p>
              <div class="mt-1 h-1 w-full bg-gray-200 rounded-full overflow-hidden">
                <div class="bg-orange-500 h-full rounded-full" [style.width]="sdgProgress.sdg9"></div>
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
export class QualiteComponent {
  // SDG images URLs
sdgImages = {
  sdg12: 'https://www.unoosa.org/images/ourwork/SDGs/E_SDG_goals_icons-individual-rgb-12.png',
  sdg16: 'https://tse3.mm.bing.net/th/id/OIP.iO0u1hr11W44JElgdKi7CQAAAA?cb=iwc1&w=446&h=440&rs=1&pid=ImgDetMain',
  sdg9: 'https://th.bing.com/th/id/R.8ce94f306d0a563e63ef0806cea47d4b?rik=WxNqGEPmI5UvBw&pid=ImgRaw&r=0'
};
  // Progress for SDG progress bars
  sdgProgress = {
    sdg12: '65%',
    sdg13: '45%',
    sdg9: '80%'
  };
  refreshSdgProgress() {
    this.sdgProgress = {
      sdg12: `${Math.round(50 + Math.random() * 40)}%`,
      sdg13: `${Math.round(40 + Math.random() * 35)}%`,
      sdg9: `${Math.round(60 + Math.random() * 30)}%`
    };
  }
}