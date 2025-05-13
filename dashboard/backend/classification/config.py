import os

class Config:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_NAME = os.getenv("DB_NAME", "SAP")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
    
    # Additional configuration parameters
    MODEL_DIR = os.getenv("MODEL_DIR", "models")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Flask configuration
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key-change-in-production")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"