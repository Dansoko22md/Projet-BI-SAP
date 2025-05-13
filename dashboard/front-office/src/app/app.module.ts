import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { RouterModule, Routes } from '@angular/router';

import { AppComponent } from './app.component';


import { CommonModule } from '@angular/common';
import { SeriePredictionFormComponent } from './dashboard/analysis/predictions/prediction-form/prediction-form.component';
import { SeriePredictionResultsComponent } from './dashboard/analysis/predictions/prediction-results/prediction-results.component';


@NgModule({
  declarations: [
  


  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    FormsModule,
    ReactiveFormsModule,
 RouterModule,
   CommonModule
  ],
  providers: [],
  bootstrap: []
})
export class AppModule { }