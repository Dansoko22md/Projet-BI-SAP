import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { ApiSerieTemporelleService, PredictionResponse } from '../../../../services/apiSerieTemporelle.service';
import { RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';
import { SeriePredictionResultsComponent } from '../prediction-results/prediction-results.component';

interface SDG {
  number: number;
  title: string;
  description: string;
}

interface MetricType {
  value: string;
  label: string;
  impactedSDGs: number[];
}

@Component({
  selector: 'app-prediction-form',
  standalone: true,
  imports: [
    FormsModule,
    ReactiveFormsModule,
    RouterModule,
    CommonModule,
    SeriePredictionResultsComponent
  ],
  templateUrl: './prediction-form.component.html',
  styleUrls: ['./prediction-form.component.scss']
})
export class SeriePredictionFormComponent implements OnInit {
  predictionForm: FormGroup;
  entities: string[] = [];
  loading = false;
  predictionResult: PredictionResponse | null = null;
  selectedMetricImpacts: SDG[] | null = null;
  
  metricTypes: MetricType[] = [
    { 
      value: 'carbon_footprint', 
      label: 'Carbon Footprint',
      impactedSDGs: [7, 11, 12, 13]
    },
    { 
      value: 'water_consumption', 
      label: 'Water Consumption',
      impactedSDGs: [6, 12, 14, 15]
    },
    { 
      value: 'energy_consumption', 
      label: 'Energy Consumption',
      impactedSDGs: [7, 9, 12, 13]
    },
    { 
      value: 'climate_co2', 
      label: 'CO2 Level',
      impactedSDGs: [11, 13, 15]
    }
  ];

  sdgs: { [key: number]: SDG } = {
    6: {
      number: 6,
      title: 'Clean Water and Sanitation',
      description: 'Ensure availability and sustainable management of water and sanitation for all'
    },
    7: {
      number: 7,
      title: 'Affordable and Clean Energy',
      description: 'Ensure access to affordable, reliable, sustainable and modern energy'
    },
    9: {
      number: 9,
      title: 'Industry, Innovation and Infrastructure',
      description: 'Build resilient infrastructure, promote inclusive and sustainable industrialization'
    },
    11: {
      number: 11,
      title: 'Sustainable Cities and Communities',
      description: 'Make cities and human settlements inclusive, safe, resilient and sustainable'
    },
    12: {
      number: 12,
      title: 'Responsible Consumption and Production',
      description: 'Ensure sustainable consumption and production patterns'
    },
    13: {
      number: 13,
      title: 'Climate Action',
      description: 'Take urgent action to combat climate change and its impacts'
    },
    14: {
      number: 14,
      title: 'Life Below Water',
      description: 'Conserve and sustainably use the oceans, seas and marine resources'
    },
    15: {
      number: 15,
      title: 'Life on Land',
      description: 'Protect, restore and promote sustainable use of terrestrial ecosystems'
    }
  };

  constructor(
    private fb: FormBuilder,
    private apiService: ApiSerieTemporelleService
  ) {
    this.predictionForm = this.fb.group({
      metric_type: ['', Validators.required],
      entity_id: [''],
      start_date: [''],
      end_date: [''],
      periods: [30, [Validators.required, Validators.min(1), Validators.max(365)]]
    });
  }

  ngOnInit(): void {
    // Initialize default dates
    const today = new Date();
    const oneYearAgo = new Date();
    oneYearAgo.setFullYear(today.getFullYear() - 1);
    
    this.predictionForm.patchValue({
      end_date: this.formatDate(today),
      start_date: this.formatDate(oneYearAgo)
    });

    // Watch for metric type changes
    this.predictionForm.get('metric_type')?.valueChanges.subscribe(metricType => {
      if (metricType) {
        this.loadEntities(metricType);
        this.updateImpactedSDGs(metricType);
      } else {
        this.selectedMetricImpacts = null;
      }
    });
  }

  formatDate(date: Date): string {
    return date.toISOString().split('T')[0];
  }

  loadEntities(metricType: string): void {
    this.entities = [];
    this.apiService.getEntities(metricType).subscribe(response => {
      if (response.success && response.entities) {
        this.entities = response.entities;
      }
    });
  }

  updateImpactedSDGs(metricType: string): void {
    const selectedMetric = this.metricTypes.find(m => m.value === metricType);
    if (selectedMetric) {
      this.selectedMetricImpacts = selectedMetric.impactedSDGs.map(sdgNumber => this.sdgs[sdgNumber]);
    } else {
      this.selectedMetricImpacts = null;
    }
  }

  onSubmit(): void {
    if (this.predictionForm.valid) {
      this.loading = true;
      this.predictionResult = null;
      
      this.apiService.predict(this.predictionForm.value).subscribe({
        next: (response) => {
          this.loading = false;
          if (response.success) {
            this.predictionResult = response;
          }
        },
        error: (error) => {
          this.loading = false;
          console.error('Error during prediction:', error);
        }
      });
    }
  }
}