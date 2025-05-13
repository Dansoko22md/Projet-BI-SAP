from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
import psycopg2
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import the configuration
from config import Config

app = Flask(__name__)

# Priority mapping
PRIORITY_MAPPING = {
    0: "Faible",
    1: "Moyenne",
    2: "Elevée",
    3: "Critique",
    4: "Inconnue"
}

PRIORITY_REVERSE_MAPPING = {v: k for k, v in PRIORITY_MAPPING.items()}

def get_db_connection():
    """Establish a connection to the PostgreSQL database"""
    try:
        conn = psycopg2.connect(
            host=Config.DB_HOST,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD
        )
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return None

def fetch_training_data():
    """Fetch data from the warehouse for model training"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        # Create a query that joins the necessary tables to get features for prediction
        query = """
        SELECT 
            n.category, 
            n.description,
            s.supplier_name, 
            s.environmental_certifications,
            s.transport_type,
            s.renewable_energy_percentage,
            e.category as equipment_category,
            e.maintenance_cycle,
            e.energy_type,
            e.estimated_lifetime_years,
            m.type as material_type,
            m.recycled_packaging,
            f.temperature_max,
            f.temperature_min,
            f.precipitations,
            f.humidity,
            f.pm2_5,
            p.stock_produced,
            f.priok as priority
        FROM "DWH".fact_maintenance_environment f
        JOIN "DWH".dim_notification n ON f.fk_notification = n.pk_notification
        JOIN "DWH".dim_supplier s ON f.fk_supplier = s.pk_supplier
        JOIN "DWH".dim_equipment e ON f.fk_equipment = e.pk_equipment
        JOIN "DWH".dim_material m ON f.fk_material = m.pk_material
        JOIN "DWH".dim_product p ON f.fk_product = p.pk_product

        WHERE f.priok IS NOT NULL
        """
        
        df = pd.read_sql(query, conn)
        logger.info(f"Fetched {len(df)} records for training")
        return df
    except Exception as e:
        logger.error(f"Error fetching training data: {e}")
        return None
    finally:
        conn.close()

def preprocess_data(df):
    """Preprocess the data for model training"""
    if df is None or df.empty:
        logger.error("No data available for preprocessing")
        return None, None
    
    # Handle missing values
    df = df.fillna({
        'supplier_name': 'Unknown',
        'environmental_certifications': 'None',
        'transport_type': 'Unknown',
        'renewable_energy_percentage': 0,
        'equipment_category': 'Unknown',
        'maintenance_cycle': 'Unknown',
        'energy_type': 'Unknown',
        'estimated_lifetime_years': 0,
        'material_type': 'Unknown',
        'recycled_packaging': False,
        'temperature_max': df['temperature_max'].median(),
        'temperature_min': df['temperature_min'].median(),
        'precipitations': df['precipitations'].median(),
        'humidity': df['humidity'].median(),
        'pm2_5': df['pm2_5'].median(),
        'stock_produced': 0,
        'category': 'Unknown',
        'description': ''
    })
    
    # Extract text features from description if needed
    # This is a simple approach; more advanced NLP could be used
    df['description_length'] = df['description'].str.len()
    
    # Define features and target
    X = df.drop(['priority', 'description'], axis=1)
    y = df['priority'].map(lambda x: min(x, 4))  # Map to 0-4 range
    
    return X, y

def build_model():
    """Build and train the prediction model"""
    df = fetch_training_data()
    if df is None:
        logger.error("Could not build model: No training data available")
        return None
    
    X, y = preprocess_data(df)
    if X is None or y is None:
        logger.error("Could not build model: Preprocessing failed")
        return None
    
    # Define categorical and numerical features
    categorical_features = [
        'category', 'supplier_name', 'environmental_certifications',
        'transport_type', 'equipment_category', 'maintenance_cycle',
        'energy_type', 'material_type'
    ]
    
    numerical_features = [
        'renewable_energy_percentage', 'estimated_lifetime_years',
        'temperature_max', 'temperature_min', 'precipitations',
        'humidity', 'pm2_5', 'stock_produced', 'description_length'
    ]
    
    binary_features = ['recycled_packaging']
    
    # Create preprocessors
    categorical_transformer = Pipeline(steps=[
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])
    
    numerical_transformer = Pipeline(steps=[
        ('scaler', StandardScaler())
    ])
    
    # Create column transformer
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', categorical_transformer, categorical_features),
            ('num', numerical_transformer, numerical_features),
            ('bin', 'passthrough', binary_features)
        ])
    
    # Create and configure the model
    model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
    ])
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train the model
    model.fit(X_train, y_train)
    
    # Evaluate the model
    y_pred = model.predict(X_test)
    logger.info("\nModel Evaluation:")
    logger.info(f"Confusion Matrix:\n {confusion_matrix(y_test, y_pred)}")
    logger.info(f"Classification Report:\n {classification_report(y_test, y_pred)}")
    
    # Save the model
    model_path = os.path.join('models', 'notification_priority_model.pkl')
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    
    logger.info(f"Model saved to {model_path}")
    return model

def load_model():
    """Load the trained model"""
    model_path = os.path.join('models', 'notification_priority_model.pkl')
    try:
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
            logger.info("Model loaded successfully")
            return model
        else:
            logger.info("No model found, building a new one")
            return build_model()
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        return None

def predict_priority(data):
    """Predict the priority of a notification"""
    model = load_model()
    if model is None:
        return {"error": "Model not available"}, 500
    
    try:
        # Convert input data to DataFrame
        input_df = pd.DataFrame([data])
        
        # Add description length
        if 'description' in input_df:
            input_df['description_length'] = input_df['description'].str.len()
        else:
            input_df['description_length'] = 0
            
        # Drop unnecessary columns
        if 'description' in input_df:
            input_df = input_df.drop(['description'], axis=1)
        
        # Make prediction
        priority_index = model.predict(input_df)[0]
        confidence = np.max(model.predict_proba(input_df)[0])
        
        priority = PRIORITY_MAPPING.get(priority_index, "Inconnue")
        
        result = {
            "predicted_priority": priority,
            "confidence": float(confidence),
            "priority_index": int(priority_index)
        }
        
        return result
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return {"error": f"Prediction error: {str(e)}"}, 500

@app.route('/')
def home():
    """Render the home page"""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """API endpoint for prediction"""
    try:
        # Get input data
        data = request.json
        
        # Validate input
        required_fields = ['category', 'supplier_name']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400
        
        # Make prediction
        result = predict_priority(data)
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"API error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/retrain', methods=['POST'])
def retrain():
    """Endpoint to retrain the model"""
    try:
        model = build_model()
        if model is None:
            return jsonify({"error": "Failed to retrain model"}), 500
        
        return jsonify({"message": "Model retrained successfully"})
    
    except Exception as e:
        logger.error(f"Retraining error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Check if model exists, if not build it
    model_path = os.path.join('models', 'notification_priority_model.pkl')
    if not os.path.exists(model_path):
        logger.info("No model found, building initial model")
        build_model()
    
    app.run(debug=True)