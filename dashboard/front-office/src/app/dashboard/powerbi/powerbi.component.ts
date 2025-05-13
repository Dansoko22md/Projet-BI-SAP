import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-powerbi',
  standalone: true,
  imports: [CommonModule],
  styleUrls: ['./powerbi.component.scss'],
  templateUrl: './powerbi.component.html',
})
export class PowerBIComponent implements OnInit {
  currentRole: string = '';
  powerBIUrl: SafeResourceUrl | null = null;

  constructor(
    private authService: AuthService,
    private sanitizer: DomSanitizer
  ) {}

  ngOnInit() {
    const user = this.authService.getCurrentUser();
    this.currentRole = user?.role || '';
    const url = this.getPowerBIUrl();
    if (url) {
      this.powerBIUrl = this.sanitizer.bypassSecurityTrustResourceUrl(url);
    }
  }

  getTitle(): string {
    const titles = {
      'admin': 'Tableau de Bord Administrateur',
      'achats': 'Tableau de Bord Achats & Production',
      'developpement': 'Tableau de Bord Développement Durable',
      'maintenance': 'Tableau de Bord Maintenance',
      'qualite': 'Tableau de Bord Qualité & Conformité'
    };
    return titles[this.currentRole as keyof typeof titles] || 'Tableau de Bord Power BI';
  }

  private getPowerBIUrl(): string {
    // Replace these URLs with your actual PowerBI embed URLs for each role
    const powerBIUrls = {
      'admin': 'https://app.powerbi.com/reportEmbed?reportId=c366dfd9-040e-45d1-b6ba-7d1adebf55f8&autoAuth=true&ctid=604f1a96-cbe8-43f8-abbf-f8eaf5d85730&filterPaneEnabled=false&navContentPaneEnabled=false',
      'achats': 'https://app.powerbi.com/reportEmbed?reportId=3a31ab74-ce8e-4347-ba1c-ba681727d727&autoAuth=true&ctid=604f1a96-cbe8-43f8-abbf-f8eaf5d85730&filterPaneEnabled=false&navContentPaneEnabled=false',
      'developpement': 'https://app.powerbi.com/reportEmbed?reportId=203b364b-3670-4a60-9e15-f93f98caefb5&autoAuth=true&ctid=604f1a96-cbe8-43f8-abbf-f8eaf5d85730&filterPaneEnabled=false&navContentPaneEnabled=false',
      'maintenance': 'https://app.powerbi.com/reportEmbed?reportId=0e601162-21ef-4e7a-8329-d766899f1fef&autoAuth=true&ctid=604f1a96-cbe8-43f8-abbf-f8eaf5d85730&filterPaneEnabled=false&navContentPaneEnabled=false',
      'qualite': 'https://app.powerbi.com/reportEmbed?reportId=53bef125-efa1-4b03-a7c7-9e641696d659&autoAuth=true&ctid=604f1a96-cbe8-43f8-abbf-f8eaf5d85730&filterPaneEnabled=false&navContentPaneEnabled=false'
    };
    return powerBIUrls[this.currentRole as keyof typeof powerBIUrls] || '';
  }
}