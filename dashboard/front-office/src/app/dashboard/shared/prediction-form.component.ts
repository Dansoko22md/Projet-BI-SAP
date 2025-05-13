import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

interface PredictionType {
  id: string;
  label: string;
  fields: Array<{
    id: string;
    label: string;
    type: string;
    placeholder: string;
    min?: number;
    max?: number;
    step?: number;
  }>;
}

interface PredictionResult {
  type: string;
  label: string;
  value: number;
  interpretation: string;
  trend: 'up' | 'down' | 'stable';
  confidence: number;
}

@Component({
  selector: 'app-prediction-form',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Form Section -->
      <div class="bg-white rounded-2xl shadow-lg overflow-hidden">
        <div class="p-6">
          <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 space-y-2 sm:space-y-0">
            <h3 class="text-xl font-bold text-gray-800">{{ title }}</h3>
            <button 
              *ngIf="showReset"
              (click)="resetData()"
              class="px-4 py-2 text-sm bg-gray-50 text-gray-600 rounded-lg hover:bg-gray-100 transition-all duration-300 flex items-center space-x-2"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              <span>Réinitialiser</span>
            </button>
          </div>

          <div class="mb-6">
            <label class="block text-sm font-medium text-gray-700 mb-2">Type de prédiction</label>
            <div class="relative">
              <select 
                [(ngModel)]="selectedPredictionType"
                (ngModelChange)="onPredictionTypeChange()"
                class="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 text-gray-700 appearance-none transition-all duration-300"
              >
                <option value="">Sélectionnez un type de prédiction</option>
                <option *ngFor="let type of predictionTypes" [value]="type.id">
                  {{ type.label }}
                </option>
              </select>
              <div class="absolute right-3 top-1/2 transform -translate-y-1/2 pointer-events-none">
                <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </div>
          </div>

          <form *ngIf="selectedPredictionType" (ngSubmit)="onSubmit()" class="space-y-4">
            <div *ngFor="let field of getCurrentFields()" class="space-y-2">
              <label [for]="field.id" class="block text-sm font-medium text-gray-700">{{ field.label }}</label>
              <div class="relative">
                <input
                  [type]="field.type"
                  [id]="field.id"
                  [name]="field.id"
                  [(ngModel)]="formData[field.id]"
                  [min]="field.min"
                  [max]="field.max"
                  [step]="field.step"
                  class="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 transition-all duration-300"
                  [placeholder]="field.placeholder"
                />
                <div class="absolute right-3 top-1/2 transform -translate-y-1/2">
                  <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                  </svg>
                </div>
              </div>
            </div>
            <button
              type="submit"
              class="w-full bg-gradient-to-r from-emerald-500 to-green-500 text-white py-3 px-6 rounded-xl hover:from-emerald-600 hover:to-green-600 transform hover:scale-[1.02] transition-all duration-300 flex items-center justify-center space-x-2 shadow-lg hover:shadow-xl"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span>Prédire</span>
            </button>
          </form>
        </div>
      </div>

      <!-- Results Section -->
      <div class="bg-white rounded-2xl shadow-lg overflow-hidden">
        <div class="p-6">
          <h3 class="text-xl font-bold text-gray-800 mb-6">Résultats de Prédiction</h3>
          
          <div *ngIf="!predictionResults.length" class="flex flex-col items-center justify-center h-64 text-gray-400">
            <div class="w-16 h-16 mb-4 rounded-full bg-gray-50 flex items-center justify-center">
              <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <p class="text-center text-gray-500">Sélectionnez un type de prédiction et entrez les données pour voir les résultats</p>
          </div>

          <div *ngIf="predictionResults.length" class="space-y-6">
            <div *ngFor="let result of predictionResults" 
                 class="bg-gray-50 rounded-xl p-6 transform transition-all duration-300 hover:scale-[1.02] hover:shadow-md">
              <!-- Result Header -->
              <div class="flex items-center justify-between mb-4">
                <h4 class="font-semibold text-gray-800">{{ result.label }}</h4>
                <div class="flex items-center space-x-2">
                  <span [class]="'text-2xl ' + (result.trend === 'up' ? 'text-emerald-500' : result.trend === 'down' ? 'text-red-500' : 'text-yellow-500')">
                    <svg *ngIf="result.trend === 'up'" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                    </svg>
                    <svg *ngIf="result.trend === 'down'" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 17h8m0 0v-8m0 8l-8-8-4 4-6-6" />
                    </svg>
                    <svg *ngIf="result.trend === 'stable'" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 12h14" />
                    </svg>
                  </span>
                  <div class="text-2xl font-bold" [class]="result.trend === 'up' ? 'text-emerald-500' : result.trend === 'down' ? 'text-red-500' : 'text-yellow-500'">
                    {{ result.value }}%
                  </div>
                </div>
              </div>
              
              <!-- Interpretation -->
              <p class="text-gray-600 text-sm mb-4">{{ result.interpretation }}</p>
              
              <!-- Confidence Bar -->
              <div class="space-y-2">
                <div class="flex justify-between items-center">
                  <span class="text-sm font-medium" [class]="result.confidence >= 80 ? 'text-emerald-600' : result.confidence >= 60 ? 'text-yellow-600' : 'text-red-600'">
                    Indice de confiance
                  </span>
                  <span class="text-sm font-semibold">{{ result.confidence }}%</span>
                </div>
                <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div class="h-full rounded-full transition-all duration-500"
                       [style.width]="result.confidence + '%'"
                       [class]="result.confidence >= 80 ? 'bg-emerald-500' : result.confidence >= 60 ? 'bg-yellow-500' : 'bg-red-500'">
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `
})
export class PredictionFormComponent {
  @Input() title: string = '';
  @Input() predictionTypes: PredictionType[] = [];
  
  @Output() onPrediction = new EventEmitter<any>();
  @Output() onReset = new EventEmitter<void>();
  
  formData: { [key: string]: any } = {};
  showReset: boolean = false;
  selectedPredictionType: string = '';
  predictionResults: PredictionResult[] = [];

  getCurrentFields() {
    if (!this.selectedPredictionType) return [];
    const type = this.predictionTypes.find(t => t.id === this.selectedPredictionType);
    return type ? type.fields : [];
  }

  onPredictionTypeChange() {
    this.formData = {};
    this.predictionResults = [];
  }

  onSubmit() {
    const type = this.predictionTypes.find(t => t.id === this.selectedPredictionType);
    if (!type) return;

    const predictions: PredictionResult[] = [];
    const numPredictions = Math.floor(Math.random() * 2) + 2;
    
    for (let i = 0; i < numPredictions; i++) {
      const value = Math.round(Math.random() * 100);
      const confidence = Math.round(50 + Math.random() * 50);
      
      let trend: 'up' | 'down' | 'stable';
      if (value > 75) trend = 'up';
      else if (value < 25) trend = 'down';
      else trend = 'stable';

      predictions.push({
        type: type.id,
        label: this.generateLabel(type.id, i),
        value,
        interpretation: this.generateInterpretation(type.id, value),
        trend,
        confidence
      });
    }

    this.predictionResults = predictions;
    this.showReset = true;
    this.onPrediction.emit({
      type: this.selectedPredictionType,
      predictions
    });
  }

  private generateLabel(type: string, index: number): string {
    const labels: { [key: string]: string[] } = {
      stocks: ['Niveau de Stock Optimal', 'Risque de Rupture', 'Coût de Stockage'],
      production: ['Taux de Production', 'Efficacité Opérationnelle', 'Qualité de Production'],
      energie: ['Consommation Énergétique', 'Efficacité Énergétique', 'Coût Énergétique'],
      maintenance: ['Risque de Panne', 'Durée de Vie Équipement', 'Coût Maintenance'],
      qualite: ['Conformité Produit', 'Satisfaction Client', 'Taux de Défauts'],
      carbone: ['Émissions CO2', 'Impact Environnemental', 'Efficacité Carbone']
    };

    return labels[type]?.[index] || `Prédiction ${index + 1}`;
  }

  private generateInterpretation(type: string, value: number): string {
    const interpretations: { [key: string]: string[] } = {
      stocks: [
        'Niveau de stock optimal atteint',
        'Risque modéré de rupture de stock',
        'Optimisation nécessaire du stock'
      ],
      production: [
        'Production optimale',
        'Amélioration possible de la production',
        'Révision du processus recommandée'
      ],
      energie: [
        'Consommation énergétique maîtrisée',
        'Optimisation énergétique possible',
        'Révision de la stratégie énergétique conseillée'
      ],
      maintenance: [
        'Équipement en bon état',
        'Maintenance préventive recommandée',
        'Intervention urgente nécessaire'
      ],
      qualite: [
        'Qualité optimale',
        'Améliorations mineures possibles',
        'Révision du processus qualité nécessaire'
      ],
      carbone: [
        'Empreinte carbone maîtrisée',
        'Optimisation possible des émissions',
        'Plan de réduction nécessaire'
      ]
    };

    const interpretationList = interpretations[type] || ['Résultat satisfaisant', 'Amélioration possible', 'Action nécessaire'];
    
    if (value >= 75) return interpretationList[0];
    if (value >= 50) return interpretationList[1];
    return interpretationList[2];
  }

  resetData() {
    this.formData = {};
    this.predictionResults = [];
    this.showReset = false;
    this.selectedPredictionType = '';
    this.onReset.emit();
  }
}