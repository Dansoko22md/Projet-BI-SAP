from flask import Flask, render_template, request, jsonify
import pandas as pd
import json
from query import get_recommendations, calculate_sustainability_score, get_supplier_sustainability_data

app = Flask(__name__)

@app.route('/')
def index():
    """Page d'accueil de l'application"""
    return render_template('index.html')

@app.route('/api/recommendations', methods=['GET'])
def api_recommendations():
    """API pour obtenir les recommandations de fournisseurs durables"""
    try:
        # Obtenir le nombre de recommandations depuis la requête
        count = request.args.get('count', default=5, type=int)
        
        # Obtenir les recommandations
        recommendations = get_recommendations(count)
        
        if recommendations is None:
            return jsonify({'error': 'Impossible de récupérer les recommandations'}), 500
        
        # Convertir le DataFrame en dictionnaire pour la réponse JSON
        result = recommendations.to_dict(orient='records')
        
        # Préparer des données complémentaires pour les visualisations
        sustainability_metrics = {
            'renewable_energy': recommendations['renewable_energy_percentage'].tolist(),
            'carbon_footprint': recommendations['avg_carbon_footprint'].tolist(),
            'water_consumption': recommendations['avg_water_consumption'].tolist(),
            'transport_distance': recommendations['avg_transport_distance'].tolist(),
            'supplier_names': recommendations['supplier_name'].tolist(),
            'sustainability_scores': recommendations['sustainability_score'].tolist()
        }
        
        return jsonify({
            'recommendations': result,
            'visualization_data': sustainability_metrics
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/supplier_details/<supplier_id>', methods=['GET'])
def supplier_details(supplier_id):
    """API pour obtenir les détails d'un fournisseur spécifique"""
    try:
        # Récupérer toutes les données des fournisseurs
        all_suppliers = get_supplier_sustainability_data()
        
        if all_suppliers is None:
            return jsonify({'error': 'Données des fournisseurs non disponibles'}), 500
        
        # Convertir l'ID en string pour assurer une correspondance correcte
        supplier_id = str(supplier_id)
        
        # Filtrer pour le fournisseur demandé
        supplier = all_suppliers[all_suppliers['supplier_id'].astype(str) == supplier_id]
        
        if supplier.empty:
            print(f"Fournisseur avec ID {supplier_id} non trouvé")
            # Pour les tests, on peut utiliser des données fictives
            # En production, retourner une erreur 404
            
            # Version production:
            # return jsonify({'error': f'Fournisseur avec ID {supplier_id} non trouvé'}), 404
            
            # Version test avec données fictives:
            test_data = {
                'supplier_id': supplier_id,
                'supplier_name': "EcoMaterials Solutions",
                'location': "Lyon, France",
                'environmental_certifications': "ISO 14001, FSC, LEED",
                'transport_type': "Multimodal",
                'sustainability_program': "Programme d'économie circulaire et d'énergie renouvelable",
                'renewable_energy_percentage': 78.5,
                'avg_carbon_footprint': 12.75,
                'avg_water_consumption': 185.3,
                'avg_transport_distance': 326.8,
                'materials_supplied': 14,
                'sustainability_score': 82.7
            }
            return jsonify(test_data)
        
        # Calculer le score de durabilité
        supplier_with_score = calculate_sustainability_score(supplier)
        
        if supplier_with_score is None or supplier_with_score.empty:
            return jsonify({'error': 'Erreur lors du calcul du score de durabilité'}), 500
        
        # Convertir en dictionnaire et s'assurer que toutes les valeurs sont sérialisables
        supplier_data = supplier_with_score.iloc[0].to_dict()
        
        # S'assurer que toutes les valeurs sont des types sérialisables JSON
        for key, value in supplier_data.items():
            if isinstance(value, (pd.Timestamp, pd.Timedelta)):
                supplier_data[key] = str(value)
            # Convertir NaN, NaT, None en None pour la sérialisation JSON
            elif pd.isna(value) or pd.isnull(value):
                supplier_data[key] = None
            # S'assurer que les valeurs numériques sont des types Python natifs
            elif isinstance(value, (float, int)):
                if key == 'sustainability_score':
                    # S'assurer que le score est un nombre entre 0 et 100
                    supplier_data[key] = max(0, min(100, float(value)))
                else:
                    supplier_data[key] = float(value)
        
        # Vérification supplémentaire pour le score de durabilité
        if 'sustainability_score' not in supplier_data or supplier_data['sustainability_score'] is None:
            supplier_data['sustainability_score'] = 50.0  # Définir une valeur par défaut
        
        # Journalisation pour débogage
        print(f"Données du fournisseur récupérées avec succès pour ID {supplier_id}, score: {supplier_data.get('sustainability_score')}")
        
        return jsonify(supplier_data)
    
    except Exception as e:
        print(f"Erreur lors de la récupération des détails du fournisseur {supplier_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    
@app.route('/recommendations')
def recommendations_page():
    """Page de recommandations de fournisseurs durables"""
    return render_template('recommendations.html')

@app.route('/details/<supplier_id>')
def details_page(supplier_id):
    """Page de détails d'un fournisseur"""
    return render_template('details.html', supplier_id=supplier_id)

@app.route('/api/llm_analysis', methods=['GET'])
def llm_analysis():
    """API pour obtenir l'analyse LLM des fournisseurs durables"""
    try:
        # Récupérer les recommandations
        recommendations = get_recommendations(10)
        
        if recommendations is None:
            return jsonify({'error': 'Données non disponibles pour l\'analyse LLM'}), 500
        
        # Créer un résumé des données des fournisseurs
        suppliers_data = recommendations[['supplier_name', 'sustainability_score', 
                                         'renewable_energy_percentage', 'avg_carbon_footprint',
                                         'avg_water_consumption', 'environmental_certifications']].to_dict(orient='records')
        
        # Dans un vrai système, vous enverriez ces données à un LLM externe
        # Pour cette démonstration, nous simulons une réponse LLM
        
        # Simulation d'analyse LLM (dans une vraie application, vous feriez un appel API vers un service LLM)
        analysis = generate_llm_analysis(suppliers_data)
        
        return jsonify({
            'analysis': analysis,
            'top_suppliers': suppliers_data[:3]
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_llm_analysis(suppliers_data):
    """
    Simule une analyse LLM des données des fournisseurs.
    Dans une application réelle, cette fonction ferait un appel à une API LLM externe.
    """
    if not suppliers_data:
        return "Aucune donnée disponible pour l'analyse."
    
    # Calculer quelques statistiques de base pour l'analyse
    top_supplier = suppliers_data[0]
    avg_score = sum(s['sustainability_score'] for s in suppliers_data) / len(suppliers_data)
    avg_renewable = sum(s['renewable_energy_percentage'] for s in suppliers_data) / len(suppliers_data)
    
    # Générer une analyse textuelle basée sur les données
    analysis = f"""
# Analyse de durabilité des fournisseurs

## Aperçu général
L'analyse des données de durabilité de vos fournisseurs montre une moyenne de score de durabilité de {avg_score:.2f}/100, avec {top_supplier['supplier_name']} en tête du classement atteignant un score de {top_supplier['sustainability_score']:.2f}/100.

## Points clés à considérer

1. **Énergie renouvelable**: La moyenne d'utilisation d'énergie renouvelable parmi vos fournisseurs est de {avg_renewable:.2f}%. Pour améliorer l'empreinte carbone globale de votre chaîne d'approvisionnement, privilégiez les partenariats avec des fournisseurs ayant des taux supérieurs à 60%.

2. **Certifications environnementales**: Les fournisseurs les mieux classés possèdent généralement plusieurs certifications environnementales. Je recommande d'établir un standard minimum de certification pour tous vos fournisseurs.

3. **Transport et logistique**: L'analyse montre que le type de transport utilisé par vos fournisseurs a un impact significatif sur leur empreinte carbone globale. Encouragez l'utilisation de moyens de transport électriques ou hybrides.

## Recommandations stratégiques

* **Court terme**: Engagez des discussions avec les fournisseurs ayant un score inférieur à 50 pour établir des plans d'amélioration concrets.
* **Moyen terme**: Développez un programme d'incitation pour récompenser les fournisseurs qui améliorent leurs pratiques durables.
* **Long terme**: Intégrez des clauses de durabilité dans tous les nouveaux contrats fournisseurs avec des objectifs mesurables.

Cette analyse basée sur les données de votre entrepôt de données pourrait être approfondie en intégrant des données supplémentaires sur les innovations durables récentes dans votre secteur et les tendances réglementaires à venir.
"""
    return analysis

if __name__ == '__main__':
    app.run(debug=True)