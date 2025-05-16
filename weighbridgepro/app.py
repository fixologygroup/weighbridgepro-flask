import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Define base model class
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy with the base class
db = SQLAlchemy(model_class=Base)

# Create the Flask app
app = Flask(__name__)

# Configure the secret key for session management
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Configure the database URI (SQLite for development, can be replaced with MySQL/PostgreSQL)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///weighbridge.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the SQLAlchemy extension
db.init_app(app)

# Import routes after initializing the app to avoid circular imports
from routes import register_routes

# Register all routes with the app
register_routes(app)

# Context processor to inject variables into all templates
@app.context_processor
def inject_globals():
    return {
        'current_year': datetime.now().year
    }

# Create database tables if they don't exist
with app.app_context():
    from models import WeighbridgeEntry, Category, Item, Setting
    db.create_all()
    
    # Initialize default settings if not already present
    if not Setting.query.filter_by(key="token_prefix").first():
        default_settings = [
            Setting(key="token_prefix", value="AB"),
            Setting(key="software_expiry", value=(datetime.now().date().isoformat())),
            Setting(key="foc_weight", value="500"),  # 500kg free on 10 tons
            Setting(key="foc_threshold", value="10000"),  # 10 tons threshold
            Setting(key="weight_unit", value="kg"),  # Default unit (kg or ton)
        ]
        db.session.bulk_save_objects(default_settings)
        db.session.commit()
    
    # Initialize default categories if not already present
    if not Category.query.first():
        default_categories = [
            Category(name="N", description="Normal"),
            Category(name="NR", description="Normal Return")
        ]
        db.session.bulk_save_objects(default_categories)
        db.session.commit()
    
    # Initialize default items if not already present
    if not Item.query.first():
        default_items = [
            Item(name="Sand", category_id=1),
            Item(name="Gravel", category_id=1),
            Item(name="Cement", category_id=1),
            Item(name="Stone", category_id=1),
            Item(name="Empty Truck", category_id=2),
        ]
        db.session.bulk_save_objects(default_items)
        db.session.commit()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
