from flask import Flask, render_template, request, jsonify
import pandas as pd
import json
from supplier_clustering import get_supplier_clusters, get_supplier_profile_with_cluster

app = Flask(__name__)

@app.route('/')
def index():
    """Page d'accueil de l'application"""
    return render_template('index.html')

@app.route('/clusters')
def clusters_page():
    """Page d'analyse des clusters de fournisseurs"""
    return render_template('clusters.html')

@app.route('/api/clusters', methods=['GET'])
def api_clusters():
    """API pour obtenir les clusters de fournisseurs"""
    try:
        # Obtenir le nombre de clusters depuis la requête
        n_clusters = request.args.get('n_clusters', default=3, type=int)
        
        # Vérifier que le nombre de clusters est valide
        if n_clusters < 2 or n_clusters > 7:
            return jsonify({'error': 'Le nombre de clusters doit être entre 2 et 7'}), 400
        
        # Obtenir les données des clusters
        clusters_data = get_supplier_clusters(n_clusters)
        
        if 'error' in clusters_data:
            return jsonify({'error': clusters_data['error']}), 500
        
        # Adapter le format de données pour correspondre à ce qu'attend le frontend
        formatted_response = {
            'clusters': [],
            'all_suppliers': [],
            'visualization': clusters_data.get('visualization')
        }
        
        # Formater les données de clusters
        for cluster in clusters_data.get('clusters', []):
            cluster_id = cluster.get('cluster_id', 0)
            
            # Extraire les statistiques moyennes
            stats = cluster.get('stats', {})
            
            formatted_cluster = {
                'cluster_id': cluster_id,
                'size': cluster.get('size', 0),
                'description': cluster.get('description', ''),
                'avg_features': {
                    'renewable_energy_percentage': stats.get('renewable_energy_percentage', 0),
                    'avg_carbon_footprint': stats.get('avg_carbon_footprint', 0),
                    'avg_water_consumption': stats.get('avg_water_consumption', 0),
                    'avg_transport_distance': stats.get('avg_transport_distance', 0),
                    'materials_supplied': stats.get('materials_supplied', 0)
                },
                'suppliers': []
            }
            
            # Ajouter les fournisseurs représentatifs
            for supplier in cluster.get('representative_suppliers', []):
                formatted_cluster['suppliers'].append({
                    'supplier_id': supplier.get('supplier_id', ''),
                    'supplier_name': supplier.get('supplier_name', f'Fournisseur {supplier.get("supplier_id", "")}')
                })
            
            formatted_response['clusters'].append(formatted_cluster)
        
        # Simuler des données pour la table complète de fournisseurs si nécessaire
        # Dans une implémentation réelle, ces données viendraient de la base de données
        df_with_clusters, _, _ = get_supplier_clusters(n_clusters, return_raw_data=True)
        
        if df_with_clusters is not None:
            for _, row in df_with_clusters.iterrows():
                formatted_response['all_suppliers'].append({
                    'supplier_id': row.get('supplier_id', ''),
                    'supplier_name': row.get('supplier_name', f'Fournisseur {row.get("supplier_id", "")}'),
                    'cluster': int(row.get('cluster', 0)) + 1,  # Ajuster pour l'affichage (commencer à 1)
                    'renewable_energy_percentage': float(row.get('renewable_energy_percentage', 0)),
                    'avg_carbon_footprint': float(row.get('avg_carbon_footprint', 0)),
                    'avg_water_consumption': float(row.get('avg_water_consumption', 0)),
                    'avg_transport_distance': float(row.get('avg_transport_distance', 0))
                })
        
        return jsonify(formatted_response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/supplier/<supplier_id>/cluster', methods=['GET'])
def api_supplier_cluster(supplier_id):
    """API pour obtenir les détails d'un fournisseur avec son cluster"""
    try:
        # Obtenir le profil du fournisseur avec son cluster
        profile_data = get_supplier_profile_with_cluster(supplier_id)
        
        if 'error' in profile_data:
            return jsonify({'error': profile_data['error']}), 404 if 'non trouvé' in profile_data['error'] else 500
        
        return jsonify(profile_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/supplier/<supplier_id>/cluster')
def supplier_cluster_page(supplier_id):
    """Page de profil d'un fournisseur avec analyse de son cluster"""
    return render_template('supplier_cluster.html', supplier_id=supplier_id)

if __name__ == '__main__':
    app.run(debug=True)