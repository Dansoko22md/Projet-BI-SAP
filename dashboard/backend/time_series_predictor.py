import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from prophet import Prophet
from sklearn.metrics import mean_squared_error, mean_absolute_error
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from sqlalchemy import create_engine
import joblib
import os
from datetime import datetime, timedelta
from config import Config

class TimeSeriesPredictor:
    """
    Classe pour la prédiction de séries temporelles environnementales et de durabilité
    """
    def __init__(self):
        self.models = {}
        self.db_url = f"postgresql+psycopg2://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}/{Config.DB_NAME}"
        self.engine = create_engine(self.db_url, connect_args={"options": "-c search_path=DWH"})
        
        # Créer le dossier pour stocker les modèles s'il n'existe pas
        os.makedirs('models', exist_ok=True)
    
    def get_time_series_data(self, metric_type, entity_id=None, start_date=None, end_date=None):
        """
        Récupère les données de séries temporelles de la base de données
        
        Args:
            metric_type: Type de métrique à récupérer (co2, energy, water, etc.)
            entity_id: ID de l'entité (fournisseur, équipement, etc.)
            start_date: Date de début pour les données
            end_date: Date de fin pour les données
            
        Returns:
            DataFrame avec les données de séries temporelles
        """
        if start_date is None:
            start_date = '2023-01-01'  # Date par défaut
        
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
            
        if metric_type == 'carbon_footprint':
            # Récupérer les données d'empreinte carbone par fournisseur
            query = f"""
            SELECT 
                d.full_date as date,
                s.supplier_name,
                AVG(f.material_carbon_footprint_per_unit_kgco2e) as carbon_footprint
            FROM 
                "DWH"."fact_maintenance_environment" f
            JOIN 
                "DWH"."dim_date" d ON f.fk_date = d.pk_date
            JOIN 
                "DWH"."dim_supplier" s ON f.fk_supplier = s.pk_supplier
            WHERE 
                d.full_date BETWEEN '{start_date}' AND '{end_date}'
            """
            
            if entity_id:
                query += f" AND s.supplier_id = '{entity_id}'"
                
            query += """
            GROUP BY 
                d.full_date, s.supplier_name
            ORDER BY 
                d.full_date
            """
            
        elif metric_type == 'water_consumption':
            # Récupérer les données de consommation d'eau par fournisseur
            query = f"""
            SELECT 
                d.full_date as date,
                s.supplier_name,
                AVG(f.material_water_consumption_per_unit_liters) as water_consumption
            FROM 
                "DWH"."fact_maintenance_environment" f
            JOIN 
                "DWH"."dim_date" d ON f.fk_date = d.pk_date
            JOIN 
                "DWH"."dim_supplier" s ON f.fk_supplier = s.pk_supplier
            WHERE 
                d.full_date BETWEEN '{start_date}' AND '{end_date}'
            """
            
            if entity_id:
                query += f" AND s.supplier_id = '{entity_id}'"
                
            query += """
            GROUP BY 
                d.full_date, s.supplier_name
            ORDER BY 
                d.full_date
            """
            
        elif metric_type == 'energy_consumption':
            # Récupérer les données de consommation d'énergie par équipement
            query = f"""
            SELECT 
                d.full_date as date,
                e.equipment_name,
                AVG(f.equipment_energy_consumption_kwh) as energy_consumption
            FROM 
                "DWH"."fact_maintenance_environment" f
            JOIN 
                "DWH"."dim_date" d ON f.fk_date = d.pk_date
            JOIN 
                "DWH"."dim_equipment" e ON f.fk_equipment = e.pk_equipment
            WHERE 
                d.full_date BETWEEN '{start_date}' AND '{end_date}'
            """
            
            if entity_id:
                query += f" AND e.equipment_id = '{entity_id}'"
                
            query += """
            GROUP BY 
                d.full_date, e.equipment_name
            ORDER BY 
                d.full_date
            """
            
        elif metric_type == 'climate_co2':
            # Récupérer les données de CO2 ambiant
            query = f"""
            SELECT 
                d.full_date as date,
                l.location_name,
                AVG(f.climate_co2_ambient_level) as co2_level
            FROM 
                "DWH"."fact_maintenance_environment" f
            JOIN 
                "DWH"."dim_date" d ON f.fk_date = d.pk_date
            JOIN 
                "DWH"."dim_location" l ON f.fk_location = l.pk_location
            WHERE 
                d.full_date BETWEEN '{start_date}' AND '{end_date}'
            """
            
            if entity_id:
                query += f" AND l.pk_location = {entity_id}"
                
            query += """
            GROUP BY 
                d.full_date, l.location_name
            ORDER BY 
                d.full_date
            """
        
        else:
            raise ValueError(f"Type de métrique non pris en charge: {metric_type}")
        
        try:
            # Exécuter la requête
            df = pd.read_sql_query(query, self.engine)
            
            if df.empty:
                print(f"Aucune donnée trouvée pour {metric_type}")
                # Générer des données synthétiques pour test
                return self._generate_synthetic_data(metric_type, entity_id, start_date, end_date)
            
            # Convertir la colonne de date en index
            df['date'] = pd.to_datetime(df['date'])
            
            return df
            
        except Exception as e:
            print(f"Erreur lors de la récupération des données: {e}")
            # Générer des données synthétiques pour test
            return self._generate_synthetic_data(metric_type, entity_id, start_date, end_date)
    
    def _generate_synthetic_data(self, metric_type, entity_id, start_date, end_date):
        """
        Génère des données synthétiques pour les tests
        """
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        
        # Créer une série de dates
        date_range = pd.date_range(start=start, end=end, freq='D')
        
        # Valeurs par défaut pour chaque métrique
        if metric_type == 'carbon_footprint':
            # Tendance à la hausse avec saisonnalité hebdomadaire
            trend = np.linspace(10, 15, len(date_range))
            seasonality = 2 * np.sin(np.arange(len(date_range)) * (2 * np.pi / 7))
            noise = np.random.normal(0, 0.5, len(date_range))
            values = trend + seasonality + noise
            entity_name = f"Fournisseur {entity_id}" if entity_id else "Tous les fournisseurs"
            
            df = pd.DataFrame({
                'date': date_range,
                'supplier_name': entity_name,
                'carbon_footprint': values
            })
            
        elif metric_type == 'water_consumption':
            # Tendance stable avec pics occasionnels
            base = 100 + np.random.normal(0, 5, len(date_range))
            # Ajouter des pics occasionnels
            for i in range(0, len(date_range), 30):
                if i < len(base):
                    base[i:i+3] = base[i:i+3] * 1.5
            entity_name = f"Fournisseur {entity_id}" if entity_id else "Tous les fournisseurs"
            
            df = pd.DataFrame({
                'date': date_range,
                'supplier_name': entity_name,
                'water_consumption': base
            })
            
        elif metric_type == 'energy_consumption':
            # Tendance saisonnière (plus élevée en hiver)
            trend = 50 + np.zeros(len(date_range))
            # Saisonnalité annuelle
            days = np.arange(len(date_range))
            seasonality = 20 * np.cos(2 * np.pi * days / 365)
            noise = np.random.normal(0, 3, len(date_range))
            values = trend + seasonality + noise
            entity_name = f"Équipement {entity_id}" if entity_id else "Tous les équipements"
            
            df = pd.DataFrame({
                'date': date_range,
                'equipment_name': entity_name,
                'energy_consumption': values
            })
            
        elif metric_type == 'climate_co2':
            # Tendance à la hausse légère avec saisonnalité journalière
            trend = np.linspace(400, 410, len(date_range))
            # Saisonnalité journalière
            days = np.arange(len(date_range))
            seasonality = 5 * np.sin(2 * np.pi * days / 1)
            noise = np.random.normal(0, 1, len(date_range))
            values = trend + seasonality + noise
            entity_name = f"Location {entity_id}" if entity_id else "Toutes les locations"
            
            df = pd.DataFrame({
                'date': date_range,
                'location_name': entity_name,
                'co2_level': values
            })
            
        else:
            # Données par défaut
            values = np.random.normal(10, 2, len(date_range))
            df = pd.DataFrame({
                'date': date_range,
                'entity_name': f"Entity {entity_id}" if entity_id else "All entities",
                'value': values
            })
        
        return df
    
    def train_model(self, df, metric_type, model_type='prophet', entity_id=None):
        """
        Entraîne un modèle de prédiction sur les données
        
        Args:
            df: DataFrame avec les données
            metric_type: Type de métrique
            model_type: Type de modèle ('prophet', 'sarima', 'exp_smoothing')
            entity_id: ID de l'entité
            
        Returns:
            Le modèle entraîné
        """
        # Définir la colonne de valeur selon le type de métrique
        if metric_type == 'carbon_footprint':
            value_col = 'carbon_footprint'
        elif metric_type == 'water_consumption':
            value_col = 'water_consumption'
        elif metric_type == 'energy_consumption':
            value_col = 'energy_consumption'
        elif metric_type == 'climate_co2':
            value_col = 'co2_level'
        else:
            value_col = 'value'
        
        # S'assurer que la colonne date est au format datetime
        df['date'] = pd.to_datetime(df['date'])
        
        if model_type == 'prophet':
            # Préparer les données pour Prophet
            prophet_df = df.rename(columns={'date': 'ds', value_col: 'y'})
            
            # Gérer les valeurs manquantes
            prophet_df = prophet_df.dropna(subset=['y'])
            
            # Créer et entraîner le modèle
            model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=False,
                changepoint_prior_scale=0.05
            )
            
            model.fit(prophet_df[['ds', 'y']])
            
        elif model_type == 'sarima':
            # Utiliser SARIMA pour les données avec saisonnalité
            # Définir l'index de date
            ts_data = df.set_index('date')[value_col]
            
            # Paramètres SARIMA (à ajuster selon les données)
            # Ordre (p,d,q) pour la partie AR, I, MA
            # Ordre saisonnier (P,D,Q,s) avec s = période saisonnière
            model = SARIMAX(
                ts_data, 
                order=(1, 1, 1),
                seasonal_order=(1, 1, 1, 7)  # Saisonnalité hebdomadaire
            )
            
            model = model.fit(disp=False)
            
        elif model_type == 'exp_smoothing':
            # Utiliser le lissage exponentiel (Holt-Winters)
            ts_data = df.set_index('date')[value_col]
            
            model = ExponentialSmoothing(
                ts_data,
                trend='add',
                seasonal='add',
                seasonal_periods=7  # Saisonnalité hebdomadaire
            )
            
            model = model.fit()
            
        else:
            raise ValueError(f"Type de modèle non pris en charge: {model_type}")
        
        # Sauvegarder le modèle
        model_id = f"{metric_type}_{entity_id}_{model_type}" if entity_id else f"{metric_type}_all_{model_type}"
        self.models[model_id] = model
        
        # Sauvegarder le modèle sur disque
        model_path = f"models/{model_id}.pkl"
        joblib.dump(model, model_path)
        
        return model
    
    def predict(self, model, periods=30, model_type='prophet', df=None, freq='D'):
        """
        Génère des prédictions à partir du modèle
        
        Args:
            model: Modèle entraîné
            periods: Nombre de périodes à prédire
            model_type: Type de modèle
            df: DataFrame original (nécessaire pour certains modèles)
            freq: Fréquence des prédictions ('D' pour jour, 'W' pour semaine, etc.)
            
        Returns:
            DataFrame avec les prédictions
        """
        if model_type == 'prophet':
            # Créer un DataFrame pour les dates futures
            future = model.make_future_dataframe(periods=periods, freq=freq)
            
            # Faire les prévisions
            forecast = model.predict(future)
            
            # Préparer le résultat
            result = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].rename(
                columns={'ds': 'date', 'yhat': 'prediction', 'yhat_lower': 'lower_bound', 'yhat_upper': 'upper_bound'}
            )
            
        elif model_type == 'sarima':
            # Prédire avec SARIMA
            pred = model.get_forecast(steps=periods)
            
            # Obtenir les intervalles de confiance
            pred_ci = pred.conf_int()
            
            # Créer le DataFrame de résultats
            last_date = df['date'].max()
            future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=periods, freq=freq)
            
            result = pd.DataFrame({
                'date': future_dates,
                'prediction': pred.predicted_mean,
                'lower_bound': pred_ci.iloc[:, 0],
                'upper_bound': pred_ci.iloc[:, 1]
            })
            
        elif model_type == 'exp_smoothing':
            # Prédire avec le lissage exponentiel
            pred = model.forecast(periods)
            
            # Créer le DataFrame de résultats
            last_date = df['date'].max()
            future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=periods, freq=freq)
            
            # Pour simplifier, on utilise un intervalle de confiance approximatif basé sur l'erreur historique
            std_dev = np.std(model.resid)
            
            result = pd.DataFrame({
                'date': future_dates,
                'prediction': pred,
                'lower_bound': pred - 1.96 * std_dev,
                'upper_bound': pred + 1.96 * std_dev
            })
            
        else:
            raise ValueError(f"Type de modèle non pris en charge: {model_type}")
        
        return result
    
    def evaluate_model(self, df, metric_type, model_type='prophet', test_size=0.2):
        """
        Évalue les performances du modèle en utilisant un ensemble de test
        
        Args:
            df: DataFrame avec toutes les données
            metric_type: Type de métrique
            model_type: Type de modèle
            test_size: Proportion des données à utiliser pour le test
            
        Returns:
            Dictionnaire avec les métriques d'évaluation
        """
        # Définir la colonne de valeur selon le type de métrique
        if metric_type == 'carbon_footprint':
            value_col = 'carbon_footprint'
        elif metric_type == 'water_consumption':
            value_col = 'water_consumption'
        elif metric_type == 'energy_consumption':
            value_col = 'energy_consumption'
        elif metric_type == 'climate_co2':
            value_col = 'co2_level'
        else:
            value_col = 'value'
        
        # Diviser les données en ensembles d'entraînement et de test
        train_size = int(len(df) * (1 - test_size))
        train_df = df.iloc[:train_size].copy()
        test_df = df.iloc[train_size:].copy()
        
        # Entraîner le modèle sur les données d'entraînement
        model = self.train_model(train_df, metric_type, model_type)
        
        # Faire des prédictions sur la période de test
        test_periods = len(test_df)
        predictions = self.predict(model, periods=test_periods, model_type=model_type, df=train_df)
        
        # Préparer les valeurs pour la comparaison
        if model_type == 'prophet':
            # Pour Prophet, nous devons filtrer les dates qui correspondent à notre ensemble de test
            pred_values = predictions[predictions['date'].isin(test_df['date'])]['prediction'].values
        else:
            # Pour les autres modèles, nous prenons directement les valeurs prédites
            pred_values = predictions['prediction'].values
        
        # Valeurs réelles de l'ensemble de test
        actual_values = test_df[value_col].values
        
        # S'assurer que les longueurs correspondent
        min_len = min(len(pred_values), len(actual_values))
        pred_values = pred_values[:min_len]
        actual_values = actual_values[:min_len]
        
        # Calculer les métriques d'évaluation
        mse = mean_squared_error(actual_values, pred_values)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(actual_values, pred_values)
        mape = np.mean(np.abs((actual_values - pred_values) / np.maximum(actual_values, 1e-10))) * 100
        
        return {
            'mse': mse,
            'rmse': rmse,
            'mae': mae,
            'mape': mape
        }
    
    def get_best_model(self, df, metric_type, entity_id=None):
        """
        Détermine le meilleur modèle pour les données
        
        Args:
            df: DataFrame avec les données
            metric_type: Type de métrique
            entity_id: ID de l'entité
            
        Returns:
            Tuple (meilleur modèle, type de modèle, métriques d'évaluation)
        """
        models_to_try = ['prophet', 'sarima', 'exp_smoothing']
        best_rmse = float('inf')
        best_model = None
        best_model_type = None
        best_metrics = None
        
        for model_type in models_to_try:
            try:
                print(f"Évaluation du modèle {model_type} pour {metric_type}")
                metrics = self.evaluate_model(df, metric_type, model_type)
                
                print(f"Métriques pour {model_type}: {metrics}")
                
                if metrics['rmse'] < best_rmse:
                    best_rmse = metrics['rmse']
                    best_model_type = model_type
                    best_metrics = metrics
                    
                    # Entraîner le modèle sur toutes les données
                    best_model = self.train_model(df, metric_type, model_type, entity_id)
                    
            except Exception as e:
                print(f"Erreur lors de l'évaluation du modèle {model_type}: {e}")
                continue
        
        return best_model, best_model_type, best_metrics
    
    def create_plot(self, historical_data, predictions, metric_type, entity_name=None):
        """
        Crée un graphique combinant les données historiques et les prévisions
        
        Args:
            historical_data: DataFrame avec les données historiques
            predictions: DataFrame avec les prédictions
            metric_type: Type de métrique
            entity_name: Nom de l'entité (pour le titre)
            
        Returns:
            Image encodée en base64
        """
        # Déterminer la colonne de valeur selon le type de métrique
        if metric_type == 'carbon_footprint':
            value_col = 'carbon_footprint'
            title = "Empreinte Carbone"
            y_label = "kg CO2e"
        elif metric_type == 'water_consumption':
            value_col = 'water_consumption'
            title = "Consommation d'Eau"
            y_label = "Litres"
        elif metric_type == 'energy_consumption':
            value_col = 'energy_consumption'
            title = "Consommation d'Énergie"
            y_label = "kWh"
        elif metric_type == 'climate_co2':
            value_col = 'co2_level'
            title = "Niveau de CO2"
            y_label = "ppm"
        else:
            value_col = 'value'
            title = "Valeur"
            y_label = "Unité"
        
        # Créer la figure
        plt.figure(figsize=(12, 6))
        
        # Tracer les données historiques
        plt.plot(historical_data['date'], historical_data[value_col], 
                 color='blue', label='Données historiques')
        
        # Tracer les prédictions
        plt.plot(predictions['date'], predictions['prediction'], 
                 color='red', linestyle='--', label='Prédictions')
        
        # Tracer l'intervalle de confiance
        plt.fill_between(predictions['date'], 
                         predictions['lower_bound'], 
                         predictions['upper_bound'], 
                         color='red', alpha=0.2, label='Intervalle de confiance (95%)')
        
        # Ajouter la légende et les étiquettes
        if entity_name:
            plt.title(f"{title} - {entity_name}")
        else:
            plt.title(title)
            
        plt.xlabel('Date')
        plt.ylabel(y_label)
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Rotation des étiquettes de l'axe x pour une meilleure lisibilité
        plt.xticks(rotation=45)
        
        # Ajuster la mise en page
        plt.tight_layout()
        
        # Convertir le graphique en image
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        
        # Encoder l'image en base64
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # Fermer la figure pour libérer la mémoire
        plt.close()
        
        return image_base64
    
    def load_model(self, metric_type, entity_id=None, model_type='prophet'):
        """
        Charge un modèle entraîné depuis le disque ou en crée un nouveau si nécessaire
        
        Args:
            metric_type: Type de métrique
            entity_id: ID de l'entité
            model_type: Type de modèle
            
        Returns:
            Le modèle chargé
        """
        model_id = f"{metric_type}_{entity_id}_{model_type}" if entity_id else f"{metric_type}_all_{model_type}"
        model_path = f"models/{model_id}.pkl"
        
        # Vérifier si le modèle existe déjà
        if os.path.exists(model_path):
            try:
                # Charger le modèle existant
                model = joblib.load(model_path)
                print(f"Modèle chargé depuis {model_path}")
                return model, model_type
            except Exception as e:
                print(f"Erreur lors du chargement du modèle: {e}")
                # Continuer et créer un nouveau modèle
        
        # Si le modèle n'existe pas ou n'a pas pu être chargé, en créer un nouveau
        print(f"Création d'un nouveau modèle pour {metric_type}")
        
        # Récupérer les données
        df = self.get_time_series_data(metric_type, entity_id)
        
        # Vérifier si assez de données pour entraîner
        if len(df) < 10:
            print("Pas assez de données pour entraîner un modèle. Génération de données synthétiques.")
            df = self._generate_synthetic_data(metric_type, entity_id, 
                                              start_date=(datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'),
                                              end_date=datetime.now().strftime('%Y-%m-%d'))
        
        # Entraîner le meilleur modèle
        if model_type == 'best':
            model, actual_model_type, _ = self.get_best_model(df, metric_type, entity_id)
            return model, actual_model_type
        else:
            # Entraîner un modèle spécifique
            model = self.train_model(df, metric_type, model_type, entity_id)
            return model, model_type


def run_prediction_pipeline(metric_type, entity_id=None, periods=30, start_date=None, end_date=None, model_type='prophet'):
    """
    Exécute le pipeline complet de prédiction
    
    Args:
        metric_type: Type de métrique
        entity_id: ID de l'entité
        periods: Nombre de périodes à prédire
        start_date: Date de début pour les données historiques
        end_date: Date de fin pour les données historiques
        model_type: Type de modèle à utiliser ('best' pour sélectionner automatiquement)
        
    Returns:
        Dictionnaire avec les résultats
    """
    try:
        # Initialiser le prédicteur
        predictor = TimeSeriesPredictor()
        
        # Récupérer les données historiques
        historical_data = predictor.get_time_series_data(
            metric_type=metric_type,
            entity_id=entity_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # Identifier l'entité
        entity_name = None
        if metric_type == 'carbon_footprint' or metric_type == 'water_consumption':
            if 'supplier_name' in historical_data.columns:
                entity_name = historical_data['supplier_name'].iloc[0] if not historical_data.empty else None
        elif metric_type == 'energy_consumption':
            if 'equipment_name' in historical_data.columns:
                entity_name = historical_data['equipment_name'].iloc[0] if not historical_data.empty else None
        elif metric_type == 'climate_co2':
            if 'location_name' in historical_data.columns:
                entity_name = historical_data['location_name'].iloc[0] if not historical_data.empty else None
        
        # Charger ou entraîner le modèle
        if model_type == 'best':
            model, actual_model_type = predictor.load_model(metric_type, entity_id, 'best')
        else:
            model, actual_model_type = predictor.load_model(metric_type, entity_id, model_type)
        
        # Faire des prédictions
        predictions = predictor.predict(
            model=model,
            periods=periods,
            model_type=actual_model_type,
            df=historical_data
        )
        
        # Créer un graphique
        plot_image = predictor.create_plot(
            historical_data=historical_data,
            predictions=predictions,
            metric_type=metric_type,
            entity_name=entity_name
        )
        
# Déterminer les tendances
        # Trouver la valeur la plus récente des données historiques
        if metric_type == 'carbon_footprint':
            value_col = 'carbon_footprint'
            latest_value = historical_data[value_col].iloc[-1] if not historical_data.empty else 0
            # Calculer la tendance (changement en pourcentage)
            if len(historical_data) > 1:
                first_value = historical_data[value_col].iloc[0]
                if first_value != 0:
                    trend_pct = ((latest_value - first_value) / first_value) * 100
                else:
                    trend_pct = 0
            else:
                trend_pct = 0
                
            # Prédiction à court terme (7 jours)
            short_term_pred = predictions['prediction'].iloc[6] if len(predictions) > 6 else None
            # Prédiction à moyen terme (30 jours)
            medium_term_pred = predictions['prediction'].iloc[-1] if not predictions.empty else None
            
        elif metric_type == 'water_consumption':
            value_col = 'water_consumption'
            latest_value = historical_data[value_col].iloc[-1] if not historical_data.empty else 0
            # Calculer la tendance
            if len(historical_data) > 1:
                first_value = historical_data[value_col].iloc[0]
                if first_value != 0:
                    trend_pct = ((latest_value - first_value) / first_value) * 100
                else:
                    trend_pct = 0
            else:
                trend_pct = 0
                
            # Prédictions
            short_term_pred = predictions['prediction'].iloc[6] if len(predictions) > 6 else None
            medium_term_pred = predictions['prediction'].iloc[-1] if not predictions.empty else None
            
        elif metric_type == 'energy_consumption':
            value_col = 'energy_consumption'
            latest_value = historical_data[value_col].iloc[-1] if not historical_data.empty else 0
            # Calculer la tendance
            if len(historical_data) > 1:
                first_value = historical_data[value_col].iloc[0]
                if first_value != 0:
                    trend_pct = ((latest_value - first_value) / first_value) * 100
                else:
                    trend_pct = 0
            else:
                trend_pct = 0
                
            # Prédictions
            short_term_pred = predictions['prediction'].iloc[6] if len(predictions) > 6 else None
            medium_term_pred = predictions['prediction'].iloc[-1] if not predictions.empty else None
            
        elif metric_type == 'climate_co2':
            value_col = 'co2_level'
            latest_value = historical_data[value_col].iloc[-1] if not historical_data.empty else 0
            # Calculer la tendance
            if len(historical_data) > 1:
                first_value = historical_data[value_col].iloc[0]
                if first_value != 0:
                    trend_pct = ((latest_value - first_value) / first_value) * 100
                else:
                    trend_pct = 0
            else:
                trend_pct = 0
                
            # Prédictions
            short_term_pred = predictions['prediction'].iloc[6] if len(predictions) > 6 else None
            medium_term_pred = predictions['prediction'].iloc[-1] if not predictions.empty else None
        
        else:
            value_col = 'value'
            latest_value = 0
            trend_pct = 0
            short_term_pred = None
            medium_term_pred = None
            
        # Déterminer l'impact environnemental et les recommandations
        impact = "neutre"
        recommendations = []
        
        if metric_type == 'carbon_footprint':
            if trend_pct > 5:
                impact = "négatif"
                recommendations = [
                    "Optimiser la chaîne d'approvisionnement pour réduire les émissions",
                    "Envisager des fournisseurs avec une meilleure empreinte carbone",
                    "Mettre en place un programme de compensation carbone"
                ]
            elif trend_pct < -5:
                impact = "positif"
                recommendations = [
                    "Continuer les pratiques actuelles qui réduisent l'empreinte carbone",
                    "Documenter les succès pour les rapports ESG",
                    "Partager les meilleures pratiques avec d'autres départements"
                ]
            else:
                recommendations = [
                    "Maintenir la surveillance des émissions",
                    "Rechercher des opportunités d'amélioration continue",
                    "Évaluer régulièrement les pratiques des fournisseurs"
                ]
                
        elif metric_type == 'water_consumption':
            if trend_pct > 5:
                impact = "négatif"
                recommendations = [
                    "Installer des systèmes de récupération d'eau",
                    "Vérifier la présence de fuites dans les systèmes",
                    "Former le personnel aux pratiques de conservation de l'eau"
                ]
            elif trend_pct < -5:
                impact = "positif"
                recommendations = [
                    "Continuer à promouvoir les pratiques de conservation de l'eau",
                    "Documenter les économies d'eau pour les rapports de durabilité",
                    "Explorer d'autres domaines pour l'efficacité hydrique"
                ]
            else:
                recommendations = [
                    "Maintenir les systèmes actuels d'économie d'eau",
                    "Surveiller régulièrement la consommation",
                    "Évaluer les possibilités d'amélioration supplémentaire"
                ]
                
        elif metric_type == 'energy_consumption':
            if trend_pct > 5:
                impact = "négatif"
                recommendations = [
                    "Réaliser un audit énergétique pour identifier les inefficacités",
                    "Remplacer les équipements anciens par des modèles à haute efficacité énergétique",
                    "Installer des systèmes de gestion automatique de l'énergie"
                ]
            elif trend_pct < -5:
                impact = "positif"
                recommendations = [
                    "Documenter les économies d'énergie pour les rapports ESG",
                    "Poursuivre les initiatives d'efficacité énergétique",
                    "Explorer l'utilisation de sources d'énergie renouvelables"
                ]
            else:
                recommendations = [
                    "Maintenir une surveillance régulière de la consommation d'énergie",
                    "Former le personnel aux bonnes pratiques énergétiques",
                    "Planifier des mises à niveau progressives des équipements"
                ]
                
        elif metric_type == 'climate_co2':
            if trend_pct > 3:
                impact = "négatif"
                recommendations = [
                    "Améliorer les systèmes de ventilation",
                    "Augmenter les plantes d'intérieur pour absorber le CO2",
                    "Vérifier les sources potentielles d'émissions de CO2"
                ]
            elif trend_pct < -3:
                impact = "positif"
                recommendations = [
                    "Maintenir les conditions actuelles de qualité de l'air",
                    "Documenter les améliorations pour les rapports de santé au travail",
                    "Partager les meilleures pratiques avec d'autres installations"
                ]
            else:
                recommendations = [
                    "Continuer à surveiller régulièrement les niveaux de CO2",
                    "S'assurer que les systèmes de ventilation sont bien entretenus",
                    "Évaluer périodiquement la qualité de l'air intérieur"
                ]
        
        # Préparer les résultats
        return {
            'success': True,
            'historical_data': {
                'dates': historical_data['date'].astype(str).tolist(),
                'values': historical_data[value_col].tolist() if value_col in historical_data.columns else []
            },
            'predictions': {
                'dates': predictions['date'].astype(str).tolist(),
                'values': predictions['prediction'].tolist(),
                'lower_bounds': predictions['lower_bound'].tolist(),
                'upper_bounds': predictions['upper_bound'].tolist()
            },
            'metrics': {
                'latest_value': float(latest_value),
                'trend_percentage': float(trend_pct),
                'short_term_prediction': float(short_term_pred) if short_term_pred is not None else None,
                'medium_term_prediction': float(medium_term_pred) if medium_term_pred is not None else None
            },
            'analysis': {
                'impact': impact,
                'recommendations': recommendations
            },
            'plot': plot_image,
            'entity_name': entity_name,
            'metric_type': metric_type,
            'model_type': actual_model_type
        }
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e)
        }

if __name__ == "__main__":
    # Test du pipeline de prédiction
    results = run_prediction_pipeline(
        metric_type='carbon_footprint',
        periods=30,
        start_date='2023-01-01',
        end_date='2024-01-01'
    )
    
    print(f"Success: {results['success']}")
    if results['success']:
        print(f"Model: {results['model_type']}")
        print(f"Latest value: {results['metrics']['latest_value']}")
        print(f"Trend: {results['metrics']['trend_percentage']}%")
        print(f"Impact: {results['analysis']['impact']}")
        print(f"Recommendations: {results['analysis']['recommendations']}")
    else:
        print(f"Error: {results['error']}")