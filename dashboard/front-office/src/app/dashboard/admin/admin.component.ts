import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { KpiCardComponent } from '../shared/kpi-card.component';
import { PredictionFormComponent } from '../shared/prediction-form.component';
import { MetricsSummaryResponse,ApiSerieTemporelleService } from '../../services/apiSerieTemporelle.service';
import { RouterModule } from '@angular/router';
import { HttpClientModule } from '@angular/common/http';
import { LoadingSpinnerComponent } from '../../loading/loading-spinner.component';

@Component({
  selector: 'app-admin',
  standalone: true,
  imports: [CommonModule, KpiCardComponent, PredictionFormComponent,RouterModule,HttpClientModule,LoadingSpinnerComponent],

  styleUrls: ['./admin.component.scss'],
  templateUrl: './admin.component.html',
})
export class AdminComponent {
  // SDG images URLs
sdgImages = {
  sdg12: 'https://www.unoosa.org/images/ourwork/SDGs/E_SDG_goals_icons-individual-rgb-12.png',
  sdg13: 'https://tse4.mm.bing.net/th/id/OIP.Q1DGxFNLY1Zj6Hl73uvr2AHaEJ?cb=iwc1&rs=1&pid=ImgDetMain',
  sdg9: 'https://th.bing.com/th/id/R.8ce94f306d0a563e63ef0806cea47d4b?rik=WxNqGEPmI5UvBw&pid=ImgRaw&r=0'
};
  // Progress for SDG progress bars
  sdgProgress = {
    sdg12: '65%',
    sdg13: '45%',
    sdg9: '80%'
  };
  loading = true;
  summaryData: MetricsSummaryResponse | null = null;
  error: string | null = null;

  constructor(private apiService: ApiSerieTemporelleService) { }

  ngOnInit(): void {
    this.loadSummaryData();
  }

  loadSummaryData(): void {
    this.loading = true;
    this.apiService.getMetricsSummary().subscribe({
      next: (response) => {
        this.loading = false;
        if (response.success) {
          this.summaryData = response;
        } else {
          this.error = response.error || 'Une erreur est survenue';
        }
      },
      error: (err) => {
        this.loading = false;
        this.error = 'Erreur de connexion au serveur';
        console.error('Erreur lors du chargement des données:', err);
      }
    });
  }
  
  // Formatter les valeurs selon le type de métrique
  formatValue(value: number, metricType: string): string {
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

  // Déterminer la classe CSS pour l'indicateur de tendance
  getTrendClass(trend: number, metricType: string): string {
    // Pour ces métriques, une baisse est positive pour l'environnement
    if (metricType === 'carbon_footprint' || metricType === 'water_consumption' || 
        metricType === 'energy_consumption' || metricType === 'climate_co2') {
      return trend > 0 ? 'text-red-600' : trend < 0 ? 'text-green-600' : 'text-gray-600';
    }
    // Pour d'autres métriques, une hausse pourrait être positive
    return trend > 0 ? 'text-green-600' : trend < 0 ? 'text-red-600' : 'text-gray-600';
  }
}