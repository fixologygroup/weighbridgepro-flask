import random
from datetime import datetime
from models import WeighbridgeEntry, Setting
from app import db

def generate_token_number():
    """
    Generates a unique token number based on the format:
    [2-char company prefix + auto-increment number] e.g. AB1001
    """
    # Get the company prefix from settings
    prefix_setting = Setting.query.filter_by(key="token_prefix").first()
    prefix = prefix_setting.value if prefix_setting else "AB"
    
    # Find the highest token number to increment
    last_entry = WeighbridgeEntry.query.order_by(WeighbridgeEntry.id.desc()).first()
    
    if last_entry and last_entry.token_number.startswith(prefix):
        # Extract the numeric part from the token
        try:
            last_number = int(last_entry.token_number[len(prefix):])
            new_number = last_number + 1
        except ValueError:
            # If there's an issue parsing the number, start from 1001
            new_number = 1001
    else:
        # If no previous entry or format changed, start from 1001
        new_number = 1001
    
    # Format the new token number
    return f"{prefix}{new_number}"

def calculate_foc(net_weight):
    """
    Calculate FOC (Free of Charge) weight based on rules and selected weight unit.
    e.g., 500kg free on 10 tons or 0.5 tons free on 10 tons
    """
    # Get the FOC settings
    foc_weight_setting = Setting.query.filter_by(key="foc_weight").first()
    foc_threshold_setting = Setting.query.filter_by(key="foc_threshold").first()
    weight_unit_setting = Setting.query.filter_by(key="weight_unit").first()
    
    foc_weight = float(foc_weight_setting.value) if foc_weight_setting else 500.0
    foc_threshold = float(foc_threshold_setting.value) if foc_threshold_setting else 10000.0
    weight_unit = weight_unit_setting.value if weight_unit_setting else "kg"
    
    # If weight unit is ton, convert values to kg for calculation
    if weight_unit == "ton":
        # Convert stored values to kg for internal calculations
        foc_weight *= 1000
        foc_threshold *= 1000
    
    # Apply FOC logic
    if net_weight >= foc_threshold:
        return foc_weight
    else:
        return 0.0

def calculate_differences(entry, loaded_weight):
    """
    Calculate net weight, FOC, and difference for an entry
    """
    # Calculate net weight (loaded - tare)
    net_weight = loaded_weight - entry.tare_weight
    
    # Calculate FOC
    foc_weight = calculate_foc(net_weight)
    
    # Calculate difference between order weight and actual net weight
    difference_weight = net_weight - entry.order_weight
    
    return {
        'loaded_weight': loaded_weight,
        'net_weight': net_weight,
        'foc_weight': foc_weight,
        'difference_weight': difference_weight
    }

def is_software_valid():
    """Check if the software is still valid based on expiry date"""
    expiry_setting = Setting.query.filter_by(key="software_expiry").first()
    
    if not expiry_setting:
        return True  # Default to valid if no setting found
    
    try:
        expiry_date = datetime.strptime(expiry_setting.value, '%Y-%m-%d').date()
        return datetime.now().date() <= expiry_date
    except ValueError:
        return True  # Default to valid if date format is incorrect

def simulate_weight_reading():
    """
    Simulates a weight reading from a weighbridge scale.
    This would be replaced with actual hardware interface code in production.
    """
    # Simulate a weight between 1000 kg and 20000 kg
    return round(random.uniform(1000, 20000), 1)
