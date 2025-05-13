import os
import numpy as np
import pandas as pd
import random
from flask import Flask, render_template, request, jsonify
import psycopg2
from psycopg2 import sql
import joblib
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import pickle
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Config:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_NAME = os.getenv("DB_NAME", "SAP")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
    MODEL_PATH = os.getenv("MODEL_PATH", "supplier_model.pkl")

class Database:
    def __init__(self):
        self.conn = None
        self.connect()
        self.ensure_data_exists()
    
    def connect(self):
        try:
            self.conn = psycopg2.connect(
                host=Config.DB_HOST,
                database=Config.DB_NAME,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD
            )
            logger.info("Database connection established successfully")
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise

    def get_suppliers_data(self):
        """Fetch supplier data from the database"""
        try:
            cursor = self.conn.cursor()
            query = sql.SQL("""
                SELECT 
                    s.pk_supplier, 
                    s.supplier_id, 
                    s.supplier_name, 
                    s.location, 
                    s.environmental_certifications, 
                    s.transport_type, 
                    s.sustainability_program,
                    s.renewable_energy_percentage,
                    COUNT(f.fk_supplier) as total_orders,
                    AVG(f.material_carbon_footprint_per_unit_kgco2e) as avg_carbon_footprint
                FROM 
                    "DWH"."dim_supplier" s
                LEFT JOIN 
                    "DWH"."fact_maintenance_environment" f ON s.pk_supplier = f.fk_supplier
                GROUP BY 
                    s.pk_supplier, s.supplier_id, s.supplier_name, s.location, 
                    s.environmental_certifications, s.transport_type, s.sustainability_program,
                    s.renewable_energy_percentage
            """)
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=columns)
            cursor.close()
            return df
        except Exception as e:
            logger.error(f"Error fetching supplier data: {e}")
            return pd.DataFrame()
            
    def get_supplier_details(self, supplier_id):
        """Get detailed information about a specific supplier"""
        try:
            cursor = self.conn.cursor()
            query = sql.SQL("""
                SELECT 
                    s.*,
                    AVG(f.material_carbon_footprint_per_unit_kgco2e) as avg_carbon_footprint,
                    AVG(f.material_transport_distance_km) as avg_transport_distance,
                    AVG(f.material_water_consumption_per_unit_liters) as avg_water_consumption
                FROM 
                    "DWH"."dim_supplier" s
                LEFT JOIN 
                    "DWH"."fact_maintenance_environment" f ON s.pk_supplier = f.fk_supplier
                WHERE 
                    s.supplier_id = %s
                GROUP BY 
                    s.pk_supplier
            """)
            cursor.execute(query, (supplier_id,))
            columns = [desc[0] for desc in cursor.description]
            data = cursor.fetchone()
            cursor.close()
            
            if data:
                return dict(zip(columns, data))
            return None
        except Exception as e:
            logger.error(f"Error fetching supplier details: {e}")
            return None
    
    def ensure_data_exists(self):
        """Check if data exists in the supplier table and create test data if it doesn't"""
        try:
            # First ensure schema and tables exist
            self.ensure_schema_exists()
            
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM DWH.dim_supplier")
            count = cursor.fetchone()[0]
            
            if count == 0:
                logger.warning("No supplier data found in database. Creating test data...")
                self.create_test_data()
            else:
                logger.info(f"Found {count} suppliers in database")
            
        except Exception as e:
            logger.error(f"Error checking for supplier data: {e}")
            # Create test data anyway
            self.create_test_data()
            
    def ensure_schema_exists(self):
        """Ensure that the DWH schema and necessary tables exist"""
        try:
            cursor = self.conn.cursor()
            
            # Create schema if not exists
            cursor.execute("CREATE SCHEMA IF NOT EXISTS DWH")
            
            # Check if supplier table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'dwh' AND table_name = 'dim_supplier'
                )
            """)
            supplier_table_exists = cursor.fetchone()[0]
            
            # Check if fact table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'dwh' AND table_name = 'fact_maintenance_environment'
                )
            """)
            fact_table_exists = cursor.fetchone()[0]
            
            if not supplier_table_exists:
                logger.info("Creating dim_supplier table...")
                cursor.execute("""
                    CREATE TABLE "DWH"."dim_supplier" (
                        pk_supplier INT PRIMARY KEY,
                        supplier_id VARCHAR(100),
                        supplier_name VARCHAR(100),
                        location VARCHAR(100),
                        contact_email VARCHAR(100),
                        phone_number VARCHAR(100),
                        environmental_certifications VARCHAR(255),
                        transport_type VARCHAR(100),
                        sustainability_program TEXT,
                        renewable_energy_percentage FLOAT
                    )
                """)
            
            if not fact_table_exists:
                logger.info("Creating fact_maintenance_environment table...")
                cursor.execute("""
                    CREATE TABLE "DWH"."fact_maintenance_environment" (
                        id SERIAL PRIMARY KEY,
                        fk_supplier INT,
                        material_carbon_footprint_per_unit_kgco2e FLOAT,
                        material_transport_distance_km FLOAT,
                        material_water_consumption_per_unit_liters FLOAT
                    )
                """)
            
            self.conn.commit()
            logger.info("Schema and tables verified/created")
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error ensuring schema and tables exist: {e}")
            raise
    
    def create_test_data(self):
        """Create test data in the database for demonstration purposes"""
        try:
            cursor = self.conn.cursor()
            
            # Create test suppliers
            suppliers = [
                (1, 'SUP001', 'EcoSupplier A', 'France', 'contact@ecosupplier.com', '+33123456789', 
                 'ISO 14001, Carbon Trust', 'Electric Vehicles', 'Comprehensive sustainability program', 85.0),
                (2, 'SUP002', 'GreenTech Industries', 'Germany', 'info@greentech.de', '+4987654321', 
                 'ISO 14001, EMAS', 'Hybrid Fleet', 'Carbon neutrality initiative', 78.0),
                (3, 'SUP003', 'Sustainable Solutions', 'Spain', 'info@sustainablesolutions.es', '+34612345678', 
                 'ISO 14001', 'Biofuel Vehicles', 'Water conservation program', 70.0),
                (4, 'SUP004', 'EcoMaterials Ltd', 'United Kingdom', 'sales@ecomaterials.co.uk', '+442071234567', 
                 'Carbon Trust', 'Rail Transport', 'Zero waste program', 65.0),
                (5, 'SUP005', 'Natural Resources Co', 'Italy', 'info@naturalresources.it', '+390123456789', 
                 'None', 'Conventional Trucks', 'Basic sustainability program', 45.0),
                (6, 'SUP006', 'Global Supplies', 'United States', 'contact@globalsupplies.com', '+15551234567', 
                 'ISO 14001', 'Mixed Fleet', 'Energy efficiency program', 60.0),
                (7, 'SUP007', 'EcoFriendly Inc', 'Canada', 'info@ecofriendly.ca', '+14165551234', 
                 'ISO 14001, LEED', 'Hybrid Fleet', 'Comprehensive sustainability program', 82.0),
                (8, 'SUP008', 'Bio Materials', 'Netherlands', 'contact@biomaterials.nl', '+31201234567', 
                 'ISO 14001, Cradle to Cradle', 'Electric Vehicles', 'Circular economy program', 88.0),
                (9, 'SUP009', 'Standard Supply Co', 'Belgium', 'info@standardsupply.be', '+3225551234', 
                 'None', 'Conventional Trucks', 'None', 30.0),
                (10, 'SUP010', 'Premium Eco Solutions', 'Switzerland', 'contact@premiumeco.ch', '+41431234567', 
                 'ISO 14001, EMAS, Carbon Trust', 'Biofuel Vehicles', 'Comprehensive sustainability program', 90.0)
            ]
            
            # Insert suppliers
            for supplier in suppliers:
                cursor.execute("""
                    INSERT INTO "DWH"."dim_supplier" (
                        pk_supplier, supplier_id, supplier_name, location, 
                        contact_email, phone_number, environmental_certifications, 
                        transport_type, sustainability_program, renewable_energy_percentage
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (pk_supplier) DO NOTHING
                """, supplier)
            
            # Create some test fact data
            for i in range(1, 30):
                supplier_id = (i % 10) + 1  # Cycle through suppliers 1-10
                cursor.execute("""
                    INSERT INTO "DWH"."fact_maintenance_environment" (
                        fk_supplier, material_carbon_footprint_per_unit_kgco2e, 
                        material_transport_distance_km, material_water_consumption_per_unit_liters
                    ) VALUES (%s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                """, (supplier_id, round(random.uniform(5, 50), 2), 
                     round(random.uniform(100, 1000), 1), round(random.uniform(10, 100), 1)))
            
            self.conn.commit()
            logger.info("Test data created successfully")
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error creating test data: {e}")
            
    def close(self):
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

class SupplierRecommender:
    def __init__(self):
        self.model = None
        self.preprocessor = None
        self.db = Database()
        
    def prepare_data(self, df):
        """Prepare data for training or prediction"""
        # Handle missing values
        df = df.fillna({
            'environmental_certifications': 'None',
            'transport_type': 'Unknown',
            'sustainability_program': 'None',
            'renewable_energy_percentage': 0,
            'total_orders': 0,
            'avg_carbon_footprint': df['avg_carbon_footprint'].mean() if 'avg_carbon_footprint' in df else 0
        })
        
        # Create target variable based on sustainability metrics
        if 'renewable_energy_percentage' in df.columns:
            df['sustainability_score'] = (
                (df['renewable_energy_percentage'] / 100) * 0.4 + 
                (df['environmental_certifications'] != 'None').astype(int) * 0.3 +
                (df['sustainability_program'] != 'None').astype(int) * 0.3
            )
            
            # Categorize into high, medium, low sustainability
            df['sustainability_level'] = pd.qcut(
                df['sustainability_score'], 
                q=3, 
                labels=['low', 'medium', 'high']
            )
        
        return df
    
    def train_model(self):
        """Train the supplier recommendation model"""
        logger.info("Starting model training...")
        try:
            # Get supplier data
            df = self.db.get_suppliers_data()
            if df.empty:
                logger.error("No data available for training")
                return False
                
            df = self.prepare_data(df)
            
            # Define features and target
            X = df.drop(['pk_supplier', 'supplier_id', 'supplier_name', 
                       'sustainability_score', 'sustainability_level'], axis=1)
            y = df['sustainability_level']
            
            # Define feature preprocessing
            categorical_features = ['location', 'environmental_certifications', 
                                  'transport_type', 'sustainability_program']
            numeric_features = ['renewable_energy_percentage', 'total_orders', 'avg_carbon_footprint']
            
            categorical_transformer = OneHotEncoder(handle_unknown='ignore')
            numeric_transformer = StandardScaler()
            
            self.preprocessor = ColumnTransformer(
                transformers=[
                    ('num', numeric_transformer, numeric_features),
                    ('cat', categorical_transformer, categorical_features)
                ])
            
            # Create and train the model
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            self.model = Pipeline(steps=[
                ('preprocessor', self.preprocessor),
                ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
            ])
            
            self.model.fit(X_train, y_train)
            
            # Save the model
            with open(Config.MODEL_PATH, 'wb') as f:
                pickle.dump(self.model, f)
            
            # Evaluate the model
            score = self.model.score(X_test, y_test)
            logger.info(f"Model trained successfully with accuracy: {score:.4f}")
            return True
            
        except Exception as e:
            logger.error(f"Error training model: {e}")
            return False
    
    def load_model(self):
        """Load the trained model"""
        try:
            if os.path.exists(Config.MODEL_PATH):
                with open(Config.MODEL_PATH, 'rb') as f:
                    self.model = pickle.load(f)
                logger.info("Model loaded successfully")
                return True
            else:
                logger.warning("Model file not found, training new model")
                return self.train_model()
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
            
    def get_default_recommendations(self):
        """Return default recommendations when all else fails"""
        try:
            # Get all suppliers and return the top ones by renewable energy percentage
            df = self.db.get_suppliers_data()
            if df.empty:
                # Create some mock data if no data exists
                return [
                    {
                        'supplier_id': 'SUP001',
                        'supplier_name': 'EcoSupplier A',
                        'location': 'France',
                        'renewable_energy_percentage': 85,
                        'sustainability_level': 'high'
                    },
                    {
                        'supplier_id': 'SUP002',
                        'supplier_name': 'GreenTech Industries',
                        'location': 'Germany',
                        'renewable_energy_percentage': 78,
                        'sustainability_level': 'high'
                    },
                    {
                        'supplier_id': 'SUP003',
                        'supplier_name': 'Sustainable Solutions',
                        'location': 'Spain',
                        'renewable_energy_percentage': 70,
                        'sustainability_level': 'medium'
                    }
                ]
            
            df = self.prepare_data(df)
            top_suppliers = df[['pk_supplier', 'supplier_id', 'supplier_name', 
                              'location', 'renewable_energy_percentage', 
                              'sustainability_level']].copy()
            
            # Sort and return top 6
            top_suppliers = top_suppliers.sort_values(
                by=['renewable_energy_percentage'], ascending=False
            ).head(6)
            
            return top_suppliers.to_dict('records')
        except Exception as e:
            logger.error(f"Error getting default recommendations: {e}")
            # Absolute fallback - hardcoded dummy data
            return [
                {
                    'supplier_id': 'SUP001',
                    'supplier_name': 'EcoSupplier A',
                    'location': 'France',
                    'renewable_energy_percentage': 85,
                    'sustainability_level': 'high'
                },
                {
                    'supplier_id': 'SUP002',
                    'supplier_name': 'GreenTech Industries',
                    'location': 'Germany',
                    'renewable_energy_percentage': 78,
                    'sustainability_level': 'high'
                }
            ]
    
    def get_supplier_recommendations(self, criteria=None):
        """Get supplier recommendations based on given criteria"""
        try:
            # Load model if not already loaded
            if self.model is None:
                if not self.load_model():
                    return []
            
            # Get all suppliers
            df = self.db.get_suppliers_data()
            if df.empty:
                return []
                
            df = self.prepare_data(df)
            
            # Extract relevant info for recommendation
            suppliers_info = df[['pk_supplier', 'supplier_id', 'supplier_name', 
                               'location', 'renewable_energy_percentage',
                               'sustainability_level']].copy()
            
            # Store original dataframe before filtering
            original_suppliers = suppliers_info.copy()
            
            # If criteria provided, filter based on it
            if criteria:
                filtered_suppliers = suppliers_info.copy()
                
                if 'location' in criteria and criteria['location']:
                    filtered_suppliers = filtered_suppliers[filtered_suppliers['location'] == criteria['location']]
                
                if 'min_renewable' in criteria and criteria['min_renewable'] is not None:
                    filtered_suppliers = filtered_suppliers[
                        filtered_suppliers['renewable_energy_percentage'] >= criteria['min_renewable']
                    ]
                    
                if 'sustainability' in criteria and criteria['sustainability']:
                    filtered_suppliers = filtered_suppliers[
                        filtered_suppliers['sustainability_level'] == criteria['sustainability']
                    ]
                
                # If we have results after filtering, use them
                # Otherwise, fall back to the original list with a relaxed filter strategy
                if not filtered_suppliers.empty:
                    suppliers_info = filtered_suppliers
                else:
                    logger.info("No exact matches found, providing alternative recommendations")
                    
                    # Apply a more relaxed filter strategy (e.g., reduce renewable requirement by 20%)
                    if 'min_renewable' in criteria and criteria['min_renewable'] is not None:
                        relaxed_renewable = max(0, criteria['min_renewable'] - 20)
                        suppliers_info = original_suppliers[
                            original_suppliers['renewable_energy_percentage'] >= relaxed_renewable
                        ]
                    
                    # If still empty, just return top suppliers from original list
                    if suppliers_info.empty:
                        suppliers_info = original_suppliers
            
            # Sort by renewable energy percentage (descending)
            suppliers_info = suppliers_info.sort_values(
                by=['renewable_energy_percentage'], ascending=False
            )
            
            # Limit to top 9 for cleaner display
            suppliers_info = suppliers_info.head(9)
            
            result = suppliers_info.to_dict('records')
            return result
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            # Return some default recommendations even if there's an error
            return self.get_default_recommendations()

