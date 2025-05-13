from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import pandas as pd
import numpy as np
import matplotlib
# Utiliser le backend 'Agg' pour éviter les problèmes avec matplotlib et les threads
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import json
import logging
from query import get_equipment_data

# Configurer le logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def prepare_equipment_data_for_clustering():
    """
    Prépare les données des équipements pour le clustering.
    
    Returns:
        tuple: (DataFrame préparé pour le clustering, DataFrame original avec les données brutes)
    """
    try:
        # Récupérer les données des équipements
        equipment_data = get_equipment_data()
        if equipment_data is None or equipment_data.empty:
            logger.error("Aucune donnée d'équipement disponible")
            return None, None
        
        # Créer une copie pour éviter de modifier le DataFrame original
        df_original = equipment_data.copy()
        
        # Sélectionner les colonnes numériques pertinentes pour le clustering
        clustering_columns = [
            'energy_consumption_kwh',
            'maintenance_cost',
            'failure_rate',
            'estimated_lifetime_years',
            'last_maintenance_days_ago',
            'downtime_hours_per_year'
        ]
        
        # Vérifier que toutes les colonnes existent
        available_columns = [col for col in clustering_columns if col in df_original.columns]
        if not available_columns:
            logger.error("Aucune colonne numérique valide pour le clustering")
            raise ValueError("Aucune colonne numérique valide pour le clustering")
        
        logger.info(f"Utilisation des colonnes pour le clustering: {available_columns}")
        
        # Créer un DataFrame nettoyé pour le clustering
        df_cluster = df_original[available_columns].copy()
        
        # Remplacer les valeurs manquantes par la médiane de chaque colonne
        for col in df_cluster.columns:
            if df_cluster[col].isna().any():
                median_value = df_cluster[col].median()
                logger.info(f"Remplacement des valeurs manquantes dans '{col}' par la médiane: {median_value}")
                df_cluster[col] = df_cluster[col].fillna(median_value)
        
        return df_cluster, df_original
    
    except Exception as e:
        logger.exception(f"Erreur lors de la préparation des données: {e}")
        return None, None

def perform_clustering(n_clusters=3):
    """
    Effectue un clustering K-means sur les données des équipements.
    
    Args:
        n_clusters: Nombre de clusters à créer
        
    Returns:
        tuple: (DataFrame avec clusters, centres des clusters, statistiques des clusters)
    """
    try:
        # Préparer les données
        df_cluster, df_original = prepare_equipment_data_for_clustering()
        if df_cluster is None:
            logger.error("Impossible de préparer les données pour le clustering")
            raise ValueError("Impossible de préparer les données pour le clustering")
        
        # Normaliser les données (très important pour K-means)
        scaler = StandardScaler()
        df_scaled = pd.DataFrame(
            scaler.fit_transform(df_cluster),
            columns=df_cluster.columns
        )
        
        # Appliquer K-means
        logger.info(f"Application de K-means avec {n_clusters} clusters")
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(df_scaled)
        
        # Ajouter les étiquettes de cluster au DataFrame original
        df_original['cluster'] = cluster_labels
        
        # Calculer les centres des clusters dans l'espace d'origine
        cluster_centers = scaler.inverse_transform(kmeans.cluster_centers_)
        
        # Créer un DataFrame des centres de clusters
        centers_df = pd.DataFrame(
            cluster_centers,
            columns=df_cluster.columns
        )
        centers_df['cluster'] = range(n_clusters)
        
        # Calculer des statistiques par cluster
        cluster_stats = df_original.groupby('cluster').agg({
            'equipment_name': 'count',
            'energy_consumption_kwh': 'mean',
            'maintenance_cost': 'mean',
            'failure_rate': 'mean',
            'estimated_lifetime_years': 'mean',
            'downtime_hours_per_year': 'mean'
        }).round(2)
        
        # Renommer la colonne des counts
        cluster_stats = cluster_stats.rename(columns={'equipment_name': 'count'})
        
        logger.info(f"Clustering terminé avec succès: {n_clusters} clusters formés")
        logger.info(f"Distribution des équipements par cluster: {df_original['cluster'].value_counts().to_dict()}")
        
        return df_original, centers_df, cluster_stats
    
    except Exception as e:
        logger.exception(f"Erreur lors du clustering: {e}")
        return None, None, None

def generate_cluster_visualization(df_with_clusters, centers_df):
    """
    Génère une visualisation des clusters en utilisant PCA pour réduire à 2 dimensions.
    
    Args:
        df_with_clusters: DataFrame avec les données et l'attribution des clusters
        centers_df: DataFrame avec les centres des clusters
        
    Returns:
        str: Image encodée en base64 de la visualisation
    """
    try:
        # Extraire les colonnes numériques (sauf 'cluster')
        numeric_cols = df_with_clusters.select_dtypes(include=[np.number]).columns.tolist()
        if 'cluster' in numeric_cols:
            numeric_cols.remove('cluster')
        
        logger.info(f"Génération de la visualisation PCA avec les colonnes: {numeric_cols}")
        
        # Appliquer PCA pour réduire à 2 dimensions
        pca = PCA(n_components=2)
        pca_result = pca.fit_transform(df_with_clusters[numeric_cols])
        
        # Réduire également les centres des clusters
        centers_pca = pca.transform(centers_df[centers_df.columns[:-1]])
        
        # Utilisation du backend 'Agg'
        plt.figure(figsize=(10, 8))
        
        # Définir une palette de couleurs
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2']
        
        # Tracer les points avec la couleur correspondant au cluster
        clusters = sorted(df_with_clusters['cluster'].unique())
        for i, cluster in enumerate(clusters):
            plt.scatter(
                pca_result[df_with_clusters['cluster'] == cluster, 0],
                pca_result[df_with_clusters['cluster'] == cluster, 1],
                s=50, c=colors[i % len(colors)], label=f'Cluster {cluster+1}'
            )
        
        # Ajouter les centres des clusters
        plt.scatter(
            centers_pca[:, 0], centers_pca[:, 1],
            s=200, c='black', marker='X', label='Centres'
        )
        
        # Ajouter des labels et une légende
        plt.title('Visualisation des clusters d\'équipements (PCA)', fontsize=15)
        plt.xlabel(f'Composante principale 1 ({(pca.explained_variance_ratio_[0]*100):.2f}%)', fontsize=12)
        plt.ylabel(f'Composante principale 2 ({(pca.explained_variance_ratio_[1]*100):.2f}%)', fontsize=12)
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Enregistrer l'image dans un buffer
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        
        # Convertir l'image en base64
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()
        
        logger.info("Visualisation générée avec succès")
        return image_base64
    
    except Exception as e:
        logger.exception(f"Erreur lors de la génération de la visualisation: {e}")
        return None

def get_equipment_clusters(n_clusters=3, return_raw_data=False):
    """
    Obtient les clusters d'équipements et leurs caractéristiques.
    
    Args:
        n_clusters: Nombre de clusters à créer
        return_raw_data: Si True, retourne également les données brutes
        
    Returns:
        dict: Données des clusters et visualisation
    """
    try:
        logger.info(f"Début de l'analyse en clusters avec {n_clusters} clusters")
        
        # Effectuer le clustering
        df_with_clusters, centers_df, cluster_stats = perform_clustering(n_clusters)
        
        if df_with_clusters is None:
            logger.error("Échec du clustering")
            return {'error': 'Échec du clustering'}
        
        # Générer la visualisation
        visualization = generate_cluster_visualization(df_with_clusters, centers_df)
        
        # Préparer les données pour chaque cluster
        clusters_data = []
        for cluster_id in range(n_clusters):
            # Filtrer les équipements de ce cluster
            cluster_equipment = df_with_clusters[df_with_clusters['cluster'] == cluster_id]
            
            # Obtenir les statistiques de ce cluster
            stats = cluster_stats.loc[cluster_id].to_dict() if cluster_id in cluster_stats.index else {}
            
            # Convertir les valeurs NaN en None pour la sérialisation JSON
            stats = {k: None if pd.isna(v) else v for k, v in stats.items()}
            
            # Trouver les équipements représentatifs (les plus proches du centre)
            representative_equipment = []
            for _, row in cluster_equipment.head(5).iterrows():
                equipment_dict = {'equipment_id': row.get('equipment_id'), 'equipment_name': row.get('equipment_name')}
                # S'assurer que les valeurs sont des types sérialisables JSON
                for key, value in equipment_dict.items():
                    if pd.isna(value):
                        equipment_dict[key] = None
                representative_equipment.append(equipment_dict)
            
            # Déterminer les caractéristiques distinctives du cluster
            cluster_center = centers_df[centers_df['cluster'] == cluster_id].iloc[0]
            distinctive_features = {}
            
            for col in centers_df.columns[:-1]:  # Exclure la colonne 'cluster'
                # Calculer l'écart par rapport à la moyenne des autres clusters
                other_centers = centers_df[centers_df['cluster'] != cluster_id]
                avg_other = other_centers[col].mean()
                this_value = cluster_center[col]
                
                # Si l'écart est significatif (arbitrairement défini comme >20%)
                difference = ((this_value - avg_other) / avg_other) * 100 if avg_other != 0 else 0
                
                if abs(difference) > 20:  # Seuil arbitraire de 20%
                    distinctive_features[col] = {
                        'value': round(float(this_value), 2),
                        'difference_percent': round(float(difference), 2),
                        'is_higher': difference > 0
                    }
            
            # Créer une description textuelle du cluster
            if distinctive_features:
                description = f"Cluster caractérisé par "
                features_list = []
                
                for feature, details in distinctive_features.items():
                    direction = "plus élevé" if details['is_higher'] else "plus bas"
                    feature_name = {
                        'energy_consumption_kwh': "consommation d'énergie",
                        'maintenance_cost': "coût de maintenance",
                        'failure_rate': "taux de défaillance",
                        'estimated_lifetime_years': "durée de vie estimée",
                        'last_maintenance_days_ago': "jours depuis la dernière maintenance",
                        'downtime_hours_per_year': "temps d'arrêt annuel"
                    }.get(feature, feature)
                    
                    features_list.append(f"{feature_name} {direction} ({details['difference_percent']}%)")
                
                description += ", ".join(features_list)
            else:
                description = "Cluster avec des caractéristiques moyennes"
            
            # Ajouter les données de ce cluster
            clusters_data.append({
                'cluster_id': cluster_id + 1,  # Pour l'affichage, commencer à 1 au lieu de 0
                'size': len(cluster_equipment),
                'description': description,
                'stats': stats,
                'representative_equipment': representative_equipment,
                'distinctive_features': distinctive_features
            })
        
        # Préparer la réponse
        response = {
            'clusters': clusters_data,
            'visualization': visualization,
            'total_equipment': len(df_with_clusters),
            'cluster_stats': {
                str(k): v for k, v in (cluster_stats.to_dict() if cluster_stats is not None else {}).items()
            }  # Convertir les clés en strings pour la sérialisation JSON
        }
        
        logger.info("Analyse en clusters terminée avec succès")
        
        # Si demandé, inclure les données brutes pour le traitement additionnel
        if return_raw_data:
            return df_with_clusters, centers_df, cluster_stats
        
        return response
    
    except Exception as e:
        logger.exception(f"Erreur lors de l'obtention des clusters: {e}")
        return {'error': str(e)}

def get_equipment_profile_with_cluster(equipment_id):
    """
    Obtient le profil d'un équipement avec son appartenance à un cluster.
    
    Args:
        equipment_id: ID de l'équipement
        
    Returns:
        dict: Données du profil de l'équipement avec son cluster
    """
    try:
        logger.info(f"Récupération du profil de l'équipement {equipment_id} avec son cluster")
        
        # Effectuer le clustering
        df_with_clusters, centers_df, _ = perform_clustering()
        
        if df_with_clusters is None:
            logger.error("Échec du clustering")
            return {'error': 'Échec du clustering'}
        
        # Convertir l'ID en string pour assurer une correspondance correcte
        equipment_id = str(equipment_id)
        
        # Trouver l'équipement spécifique
        equipment = df_with_clusters[df_with_clusters['equipment_id'].astype(str) == equipment_id]
        
        if equipment.empty:
            logger.warning(f"Équipement avec ID {equipment_id} non trouvé")
            return {'error': f'Équipement avec ID {equipment_id} non trouvé'}
        
        # Obtenir le cluster de l'équipement
        cluster_id = int(equipment['cluster'].iloc[0])
        
        # Obtenir les données de l'équipement
        equipment_data = equipment.iloc[0].to_dict()
        
        # S'assurer que toutes les valeurs sont des types sérialisables JSON
        for key, value in equipment_data.items():
            if isinstance(value, (pd.Timestamp, pd.Timedelta)):
                equipment_data[key] = str(value)
            # Convertir NaN, NaT, None en None pour la sérialisation JSON
            elif pd.isna(value) or pd.isnull(value):
                equipment_data[key] = None
        
        # Trouver les autres équipements du même cluster
        same_cluster_equipment = df_with_clusters[
            (df_with_clusters['cluster'] == cluster_id) & 
            (df_with_clusters['equipment_id'].astype(str) != equipment_id)
        ].head(5)[['equipment_id', 'equipment_name']].to_dict('records')
        
        # Assurer que les données sont sérialisables
        for equipment in same_cluster_equipment:
            for key, value in equipment.items():
                if pd.isna(value):
                    equipment[key] = None
        
        # Préparer la réponse
        response = {
            'equipment': equipment_data,
            'cluster_id': cluster_id + 1,  # Pour l'affichage, commencer à 1 au lieu de 0
            'similar_equipment': same_cluster_equipment
        }
        
        logger.info(f"Profil de l'équipement {equipment_id} récupéré avec succès (Cluster {cluster_id+1})")
        return response
    
    except Exception as e:
        logger.exception(f"Erreur lors de la récupération du profil avec cluster: {e}")
        return {'error': str(e)}

if __name__ == "__main__":
    # Pour tester la fonction
    try:
        clusters = get_equipment_clusters(3)
        if 'error' not in clusters:
            logger.info(f"Test réussi: {len(clusters['clusters'])} clusters générés")
        else:
            logger.error(f"Test échoué: {clusters['error']}")
    except Exception as e:
        logger.exception(f"Erreur lors du test: {e}")