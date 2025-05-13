from sqlalchemy import create_engine
import pandas as pd
from config import Config
import psycopg2

def get_supplier_sustainability_data():
    try:
        # Construction de l'URL de connexion SQLAlchemy
        db_url = f"postgresql+psycopg2://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}/{Config.DB_NAME}"
        
        # Ajout du schéma par défaut dans le paramètre connect_args
        engine = create_engine(db_url, connect_args={"options": "-c search_path=DWH"})
        
        query = """
        SELECT 
            s.supplier_id,
            s.supplier_name,
            s.location,
            s.environmental_certifications,
            s.transport_type,
            s.sustainability_program,
            s.renewable_energy_percentage,
            AVG(f.material_carbon_footprint_per_unit_kgco2e) as avg_carbon_footprint,
            AVG(f.material_water_consumption_per_unit_liters) as avg_water_consumption,
            AVG(f.material_transport_distance_km) as avg_transport_distance,
            COUNT(DISTINCT f.fk_material) as materials_supplied
        FROM 
            "DWH"."dim_supplier" s
        JOIN 
            "DWH"."fact_maintenance_environment" f ON s.pk_supplier = f.fk_supplier
        GROUP BY 
            s.supplier_id, s.supplier_name, s.location, s.environmental_certifications, 
            s.transport_type, s.sustainability_program, s.renewable_energy_percentage
        ORDER BY 
            s.renewable_energy_percentage DESC,
            avg_carbon_footprint ASC
        """
        
        # Utilisation du moteur SQLAlchemy
        df = pd.read_sql_query(query, engine)
        
        if df.empty:
            raise ValueError("Aucune donnée de fournisseur récupérée.")
        
        print(f"Données récupérées: {len(df)} fournisseurs")
        return df

    except Exception as e:
        print(f"Erreur lors de la récupération des données de fournisseurs: {e}")
        return None
    
def calculate_sustainability_score(supplier_data):
    """
    Calcule un score de durabilité pour chaque fournisseur basé sur plusieurs critères.
    
    Le score est calculé sur une échelle de 0 à 100, où 100 est le meilleur score.
    """
    if supplier_data is None or supplier_data.empty:
        return None
    
    # Créer une copie pour éviter de modifier le DataFrame original
    df = supplier_data.copy()
    
    # Normalisation des valeurs numériques (min-max scaling)
    numeric_columns = ['renewable_energy_percentage', 'avg_carbon_footprint', 
                      'avg_water_consumption', 'avg_transport_distance']
    
    for col in numeric_columns:
        if col in df.columns:
            if col == 'renewable_energy_percentage':
                # Pour l'énergie renouvelable, plus c'est élevé, mieux c'est
                df[f'{col}_score'] = (df[col] - df[col].min()) / (df[col].max() - df[col].min()) * 25
            else:
                # Pour les autres métriques, plus c'est bas, mieux c'est
                df[f'{col}_score'] = (1 - (df[col] - df[col].min()) / (df[col].max() - df[col].min())) * 15
    
    # Score pour les certifications environnementales (bonus de 10 points)
    df['cert_score'] = df['environmental_certifications'].apply(
        lambda x: min(10, 2 * len(x.split(',')) if isinstance(x, str) and x.strip() else 0)
    )
    
    # Score pour le type de transport (10 points maximum)
    transport_scores = {
    'Maritime': 10,      # Très efficace pour le transport de masse à longue distance, faible empreinte carbone par tonne-km
    'Ferroviaire': 8,    # Très durable, peu d’émissions, mais infrastructure limitée
    'Camionnage': 5,     # Moyen en durabilité, souple mais plus polluant que maritime/ferroviaire
    'Multimodal': 4,     # Combine plusieurs modes (souvent complexe), mais peut être optimisé
    'Aérien': 2,         # Très polluant, utilisé pour rapidité mais mauvais pour la durabilité
    'Unknown': 1         # Donnée manquante ou inconnue → score minimal par prudence
    }
    df['transport_score'] = df['transport_type'].apply(
        lambda x: transport_scores.get(x.lower(), 0) if isinstance(x, str) else 0
    )
    
    # Score pour le programme de durabilité (10 points)
    df['program_score'] = df['sustainability_program'].apply(
        lambda x: 10 if isinstance(x, str) and len(x.strip()) > 10 else 0
    )
    
    # Calcul du score total
    score_columns = [col for col in df.columns if col.endswith('_score')]
    df['sustainability_score'] = df[score_columns].sum(axis=1)
    
    # Normalisation du score final de 0 à 100
    max_possible = 100  # Score maximum théorique
    df['sustainability_score'] = (df['sustainability_score'] / max_possible) * 100
    df['sustainability_score'] = df['sustainability_score'].clip(0, 100)  # Limiter entre 0 et 100
    
    # Arrondir à 2 décimales
    df['sustainability_score'] = df['sustainability_score'].round(2)
    
    return df.sort_values('sustainability_score', ascending=False)

def get_recommendations(top_n=5):
    """
    Récupère les recommandations des fournisseurs les plus durables.
    
    Args:
        top_n: Nombre de fournisseurs à recommander.
    
    Returns:
        DataFrame contenant les recommandations.
    """
    supplier_data = get_supplier_sustainability_data()
    if supplier_data is None:
        return None
    
    scored_suppliers = calculate_sustainability_score(supplier_data)
    if scored_suppliers is None:
        return None
    
    # Sélectionner les top N fournisseurs les plus durables
    top_suppliers = scored_suppliers.head(top_n)
    
    return top_suppliers

# Pour tester le script indépendamment
if __name__ == "__main__":
    recommendations = get_recommendations(10)
    if recommendations is not None:
        print("\nTop 10 fournisseurs durables recommandés:")
        print(recommendations[['supplier_name', 'sustainability_score', 'renewable_energy_percentage', 
                               'environmental_certifications', 'transport_type']].to_string(index=False))