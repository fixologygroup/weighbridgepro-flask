from datetime import datetime
from app import db

class WeighbridgeEntry(db.Model):
    """Model for weighbridge entries (both in-time and out-time)"""
    id = db.Column(db.Integer, primary_key=True)
    token_number = db.Column(db.String(10), unique=True, nullable=False)
    vehicle_number = db.Column(db.String(20), nullable=False)
    driver_name = db.Column(db.String(100), nullable=False)
    mobile_number = db.Column(db.String(15), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    order_weight = db.Column(db.Float, nullable=False)
    tare_weight = db.Column(db.Float, nullable=False)
    loaded_weight = db.Column(db.Float, nullable=True)
    net_weight = db.Column(db.Float, nullable=True)
    foc_weight = db.Column(db.Float, nullable=True)
    difference_weight = db.Column(db.Float, nullable=True)
    in_time = db.Column(db.DateTime, default=datetime.now, nullable=False)
    out_time = db.Column(db.DateTime, nullable=True)
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    category = db.relationship('Category', backref=db.backref('entries', lazy=True))
    item = db.relationship('Item', backref=db.backref('entries', lazy=True))
    
    def __repr__(self):
        return f'<WeighbridgeEntry {self.token_number}>'

class Category(db.Model):
    """Model for vehicle categories (N, NR, etc.)"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f'<Category {self.name}>'

class Item(db.Model):
    """Model for items (sand, gravel, etc.)"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    category = db.relationship('Category', backref=db.backref('items', lazy=True))
    
    def __repr__(self):
        return f'<Item {self.name}>'

class Setting(db.Model):
    """Model for system settings (token prefix, software validity, etc.)"""
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f'<Setting {self.key}: {self.value}>'

class User(db.Model):
    """Model for users (admin, operators)"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f'<User {self.username}>'
