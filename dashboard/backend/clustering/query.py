from sqlalchemy import create_engine
import pandas as pd
from config import Config
import psycopg2
import traceback

def get_supplier_sustainability_data():
    """
    Récupère les données de durabilité des fournisseurs depuis la base de données.
    
    Returns:
        DataFrame: Données des fournisseurs avec leurs métriques de durabilité
    """
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
            "DWH".dim_supplier s
        JOIN 
            "DWH".fact_maintenance_environment f ON s.pk_supplier = f.fk_supplier
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
        traceback.print_exc()  # Afficher la trace complète pour le débogage
        return None

def get_equipment_data():
    """
    Récupère les données des équipements depuis la base de données.
    
    Returns:
        DataFrame: Données des équipements avec leurs métriques de maintenance et performance
    """
    try:
        # Construction de l'URL de connexion SQLAlchemy
        db_url = f"postgresql+psycopg2://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}/{Config.DB_NAME}"
        
        # Ajout du schéma par défaut dans le paramètre connect_args
        engine = create_engine(db_url, connect_args={"options": "-c search_path=DWH"})
        
        query = """
        SELECT 
            e.pk_equipment,
            e.equipment_id,
            e.equipment_name,
            e.category,
            e.maintenance_cycle,
            e.location,
            e.manufacturer,
            e.energy_type,
            e.maintenance_frequency,
            e.estimated_lifetime_years,
            AVG(f.energy_consumption_kwh) as energy_consumption_kwh,
            AVG(f.maintenance_cost) as maintenance_cost,
            AVG(f.failure_rate) as failure_rate,
            MAX(EXTRACT(DAY FROM (CURRENT_DATE - f.last_maintenance_date))) as last_maintenance_days_ago,
            SUM(f.downtime_hours) / COUNT(DISTINCT EXTRACT(YEAR FROM f.maintenance_date)) as downtime_hours_per_year
        FROM 
            "DWH".dim_equipment e
        JOIN 
            "DWH".fact_maintenance_environment f ON e.pk_equipment = f.fk_equipment
        GROUP BY 
            e.pk_equipment, e.equipment_id, e.equipment_name, e.category, e.maintenance_cycle,
            e.location, e.manufacturer, e.energy_type, e.maintenance_frequency, e.estimated_lifetime_years
        ORDER BY 
            e.category,
            e.manufacturer
        """
        
        # Utilisation du moteur SQLAlchemy
        df = pd.read_sql_query(query, engine)
        
        if df.empty:
            raise ValueError("Aucune donnée d'équipement récupérée.")
        
        print(f"Données récupérées: {len(df)} équipements")
        return df
    except Exception as e:
        print(f"Erreur lors de la récupération des données d'équipements: {e}")
        traceback.print_exc()  # Afficher la trace complète pour le débogage
        return None

def test_database_connection():
    """
    Teste la connexion à la base de données.
    
    Returns:
        bool: True si la connexion est réussie, False sinon
    """
    try:
        # Connexion à PostgreSQL
        conn = psycopg2.connect(
            host=Config.DB_HOST,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD
        )
        
        # Créer un curseur
        cursor = conn.cursor()
        
        # Exécuter une requête simple
        cursor.execute("SELECT 1")
        
        # Récupérer le résultat
        result = cursor.fetchone()
        
        # Fermer la connexion
        cursor.close()
        conn.close()
        
        if result and result[0] == 1:
            print("Connexion à la base de données réussie!")
            return True
        else:
            print("La connexion à la base de données a échoué")
            return False
        
    except Exception as e:
        print(f"Erreur lors de la connexion à la base de données: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Tester la connexion à la base de données
    if test_database_connection():
        # Si la connexion réussit, récupérer les données
        supplier_df = get_supplier_sustainability_data()
        equipment_df = get_equipment_data()
        
        if supplier_df is not None:
            print("Données fournisseurs:")
            print(supplier_df.head())
            print(f"Colonnes du DataFrame des fournisseurs: {supplier_df.columns.tolist()}")
        else:
            print("Impossible de récupérer les données des fournisseurs")
            
        if equipment_df is not None:
            print("\nDonnées équipements:")
            print(equipment_df.head())
            print(f"Colonnes du DataFrame des équipements: {equipment_df.columns.tolist()}")
        else:
            print("Impossible de récupérer les données des équipements")
    else:
        print("Veuillez vérifier vos paramètres de connexion à la base de données dans config.py")