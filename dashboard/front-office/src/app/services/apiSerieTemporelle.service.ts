import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

export interface PredictionParams {
  metric_type: string;
  entity_id?: string;
  periods?: number;
  start_date?: string;
  end_date?: string;
}

export interface EntityResponse {
  success: boolean;
  entities?: string[];
  error?: string;
}

export interface PredictionResponse {
  success: boolean;
  plot: string;
  entity_name: string;
  metric_type: string;
  metrics: {
    latest_value: number;
    trend_percentage: number;
    short_term_prediction: number;
    medium_term_prediction: number;
  };
  analysis: {
    impact: string;
    recommendations: string[];
  };
  error?: string;
}

export interface MetricsSummaryResponse {
  success: boolean;
  summary?: {
    carbon_footprint: MetricSummary;
    water_consumption: MetricSummary;
    energy_consumption: MetricSummary;
    climate_co2: MetricSummary;
  };
  error?: string;
}

interface MetricSummary {
  avg: number;
  trend: number;
  last_value: number;
}

@Injectable({
  providedIn: 'root'
})
export class ApiSerieTemporelleService {
  private apiUrl = 'http://127.0.0.1:5000';

  constructor(private http: HttpClient) {}

  // Récupérer la liste des entités pour un type de métrique donné
  getEntities(metricType: string): Observable<EntityResponse> {
    return this.http.get<EntityResponse>(`${this.apiUrl}/entities`, {
      params: { metric_type: metricType }
    });
  }

  // Générer des prédictions basées sur les paramètres fournis
  predict(params: PredictionParams): Observable<PredictionResponse> {
    const formData = new FormData();
    
    formData.append('metric_type', params.metric_type);
    
    if (params.entity_id) {
      formData.append('entity_id', params.entity_id);
    }
    
    if (params.periods) {
      formData.append('periods', params.periods.toString());
    }
    
    if (params.start_date) {
      formData.append('start_date', params.start_date);
    }
    
    if (params.end_date) {
      formData.append('end_date', params.end_date);
    }
    
    return this.http.post<PredictionResponse>(`${this.apiUrl}/predict`, formData);
  }

  // Récupérer un résumé des métriques environnementales
  getMetricsSummary(): Observable<MetricsSummaryResponse> {
    return this.http.get<MetricsSummaryResponse>(`${this.apiUrl}/metrics-summary`);
  }
}