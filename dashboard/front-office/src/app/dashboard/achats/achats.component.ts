import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { KpiCardComponent } from '../shared/kpi-card.component';
import { PredictionFormComponent } from '../shared/prediction-form.component';

@Component({
  selector: 'app-achats',
  standalone: true,
  imports: [CommonModule, KpiCardComponent, PredictionFormComponent],
  templateUrl: './achats.component.html',
})
export class AchatsComponent {
  initialKpis = {
    stocks: '85%',
    efficacite: '92%',
    fournisseurs: '78%'
  };

  kpis = { ...this.initialKpis };

  updating = {
    stocks: false,
    efficacite: false,
    fournisseurs: false
  };
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
  updateKPIs(event: any) {
    Object.keys(this.updating).forEach(key => this.updating[key as keyof typeof this.updating] = true);
    
    setTimeout(() => {
      this.kpis = {
        stocks: `${Math.round(80 + Math.random() * 15)}%`,
        efficacite: `${Math.round(85 + Math.random() * 10)}%`,
        fournisseurs: `${Math.round(75 + Math.random() * 20)}%`
      };
      
      Object.keys(this.updating).forEach(key => this.updating[key as keyof typeof this.updating] = false);
    }, 500);
  }

  resetKPIs() {
    Object.keys(this.updating).forEach(key => this.updating[key as keyof typeof this.updating] = true);
    
    setTimeout(() => {
      this.kpis = { ...this.initialKpis };
      Object.keys(this.updating).forEach(key => this.updating[key as keyof typeof this.updating] = false);
    }, 500);
  }

  refreshSdgProgress() {
    this.sdgProgress = {
      sdg12: `${Math.round(50 + Math.random() * 40)}%`,
      sdg13: `${Math.round(40 + Math.random() * 35)}%`,
      sdg9: `${Math.round(60 + Math.random() * 30)}%`
    };
  }
}