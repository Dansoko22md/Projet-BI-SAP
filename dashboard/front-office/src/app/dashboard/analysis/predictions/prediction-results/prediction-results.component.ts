import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { PredictionResponse } from '../../../../services/apiSerieTemporelle.service';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-prediction-results',
    standalone: true,
     imports: [
        FormsModule,
        ReactiveFormsModule,
        RouterModule,
        CommonModule,
        
      ],
  templateUrl: './prediction-results.component.html',
  styleUrls: ['./prediction-results.component.scss']
})
export class SeriePredictionResultsComponent implements OnChanges {
  @Input() predictionData: PredictionResponse | null = null;
  
  constructor() { }

  ngOnChanges(changes: SimpleChanges): void {
    // Réactions aux changements des données de prédiction
    if (changes['predictionData'] && this.predictionData) {
      // Vous pourriez ajouter un traitement ici si nécessaire
    }
  }

  // Formatter les valeurs selon le type de métrique
  formatValue(value: number | null, metricType: string): string {
    if (value === null || value === undefined) return '--';
    
    switch (metricType) {
      case 'carbon_footprint':
        return `${value.toFixed(2)} kg CO2e`;
      case 'water_consumption':
        return `${value.toFixed(2)} L`;
      case 'energy_consumption':
        return `${value.toFixed(2)} kWh`;
      case 'climate_co2':
        return `${value.toFixed(2)} ppm`;
      default:
        return value.toFixed(2);
    }
  }

  // Déterminer les classes CSS pour la tendance
  getTrendClass(trend: number, metricType: string): string {
    if (metricType === 'carbon_footprint' || metricType === 'water_consumption' || 
        metricType === 'energy_consumption' || metricType === 'climate_co2') {
      return trend > 0 ? 'text-red-600' : trend < 0 ? 'text-green-600' : 'text-gray-600';
    }
    return trend > 0 ? 'text-green-600' : trend < 0 ? 'text-red-600' : 'text-gray-600';
  }

  // Déterminer la classe CSS pour l'indicateur d'impact
  getImpactClass(impact: string): string {
    switch (impact.toLowerCase()) {
      case 'positif':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'neutre':
        return 'bg-gray-100 text-gray-800 border-gray-200';
      case 'négatif':
      case 'negatif':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  }
}