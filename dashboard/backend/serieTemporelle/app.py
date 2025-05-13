import os
from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import pandas as pd
from werkzeug.middleware.proxy_fix import ProxyFix

# Importer le prédicteur
from time_series_predictor import TimeSeriesPredictor, run_prediction_pipeline

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

# Configuration du dossier pour les templates et les fichiers statiques
app.template_folder = 'templates'
app.static_folder = 'static'

# Vérifier que le dossier de modèles existe
os.makedirs('models', exist_ok=True)

@app.route('/')
def index():
    """Page d'accueil avec le formulaire de prédiction"""
    return render_template('index2.html')

@app.route('/predict', methods=['POST'])
def predict():
    """Endpoint pour générer des prédictions"""
    try:
        # Récupérer les paramètres du formulaire
        metric_type = request.form.get('metric_type')
        entity_id = request.form.get('entity_id')
        periods = int(request.form.get('periods', 30))
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        
        # Valider les entrées
        if not metric_type:
            return jsonify({'success': False, 'error': 'Type de métrique requis'})
        
        # Si entity_id est vide, le mettre à None
        if not entity_id or entity_id.strip() == '':
            entity_id = None
        
        # Exécuter le pipeline de prédiction
        results = run_prediction_pipeline(
            metric_type=metric_type,
            entity_id=entity_id,
            periods=periods,
            start_date=start_date,
            end_date=end_date
        )
        
        return jsonify(results)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/entities', methods=['GET'])
def get_entities():
    """Endpoint pour récupérer la liste des entités disponibles par type de métrique"""
    try:
        metric_type = request.args.get('metric_type')
        
        if not metric_type:
            return jsonify({'success': False, 'error': 'Type de métrique requis'})
        
        # Initialiser le prédicteur
        predictor = TimeSeriesPredictor()
        
        # Récupérer les données pour identifier les entités disponibles
        df = predictor.get_time_series_data(metric_type)
        
        entities = []
        
        if metric_type == 'carbon_footprint' or metric_type == 'water_consumption':
            if 'supplier_name' in df.columns:
                entities = df['supplier_name'].unique().tolist()
        elif metric_type == 'energy_consumption':
            if 'equipment_name' in df.columns:
                entities = df['equipment_name'].unique().tolist()
        elif metric_type == 'climate_co2':
            if 'location_name' in df.columns:
                entities = df['location_name'].unique().tolist()
        
        return jsonify({
            'success': True,
            'entities': entities
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/dashboard')
def dashboard():
    """Page de tableau de bord avec des statistiques générales"""
    return render_template('dashboard.html')

@app.route('/metrics-summary', methods=['GET'])
def metrics_summary():
    """Endpoint pour obtenir un résumé des métriques environnementales"""
    try:
        # Initialiser le prédicteur
        predictor = TimeSeriesPredictor()
        
        # Date de fin (aujourd'hui)
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        # Date de début (1 an en arrière)
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        
        # Récupérer les données pour chaque métrique
        carbon_data = predictor.get_time_series_data('carbon_footprint', start_date=start_date, end_date=end_date)
        water_data = predictor.get_time_series_data('water_consumption', start_date=start_date, end_date=end_date)
        energy_data = predictor.get_time_series_data('energy_consumption', start_date=start_date, end_date=end_date)
        co2_data = predictor.get_time_series_data('climate_co2', start_date=start_date, end_date=end_date)
        
        # Calculer les moyennes, tendances, etc.
        summary = {
            'carbon_footprint': {
                'avg': round(carbon_data['carbon_footprint'].mean(), 2) if 'carbon_footprint' in carbon_data else 0,
                'trend': _calculate_trend(carbon_data, 'carbon_footprint') if 'carbon_footprint' in carbon_data else 0,
                'last_value': round(carbon_data['carbon_footprint'].iloc[-1], 2) if 'carbon_footprint' in carbon_data.columns and len(carbon_data) > 0 else 0
            },
            'water_consumption': {
                'avg': round(water_data['water_consumption'].mean(), 2) if 'water_consumption' in water_data else 0,
                'trend': _calculate_trend(water_data, 'water_consumption') if 'water_consumption' in water_data else 0,
                'last_value': round(water_data['water_consumption'].iloc[-1], 2) if 'water_consumption' in water_data.columns and len(water_data) > 0 else 0
            },
            'energy_consumption': {
                'avg': round(energy_data['energy_consumption'].mean(), 2) if 'energy_consumption' in energy_data else 0,
                'trend': _calculate_trend(energy_data, 'energy_consumption') if 'energy_consumption' in energy_data else 0,
                'last_value': round(energy_data['energy_consumption'].iloc[-1], 2) if 'energy_consumption' in energy_data.columns and len(energy_data) > 0 else 0
            },
            'climate_co2': {
                'avg': round(co2_data['co2_level'].mean(), 2) if 'co2_level' in co2_data else 0,
                'trend': _calculate_trend(co2_data, 'co2_level') if 'co2_level' in co2_data else 0,
                'last_value': round(co2_data['co2_level'].iloc[-1], 2) if 'co2_level' in co2_data.columns and len(co2_data) > 0 else 0
            }
        }
        
        return jsonify({
            'success': True,
            'summary': summary
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})

def _calculate_trend(df, column):
    """Calcule la tendance d'une série de données (pourcentage de variation)"""
    if column not in df.columns or len(df) < 2:
        return 0
    
    # Prendre les 30 derniers jours si disponibles
    recent_data = df.iloc[-30:] if len(df) > 30 else df
    
    # Calculer la variation en pourcentage
    first_value = recent_data[column].iloc[0]
    last_value = recent_data[column].iloc[-1]
    
    if first_value == 0:
        return 0
    
    return round(((last_value - first_value) / first_value) * 100, 2)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)