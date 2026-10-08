import os
from flask import Flask, jsonify
from database import db, init_db

# Interface 1 & Common Blueprints
from auth_routes import auth_bp
from farmer_profile_routes import farmer_profile_bp
from fpo_routes import fpo_profile_bp
from listing_routes import listings_bp
from order_routes import orders_bp
from analytics_routes import analytics_bp
from utils_routes import utils_bp

# Interface 2 Blueprints
from buyer_auth_routes import buyer_auth_bp
from buyer_portal_routes import buyer_portal_bp

# Interface 3 Blueprints
from driver_auth_routes import driver_auth_bp
from driver_portal_routes import driver_portal_bp

# Interface 4 Blueprints
from admin_auth_routes import admin_auth_bp
from admin_portal_routes import admin_portal_bp

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'super_secret_farm_key_2026')

# MySQL Database Configuration
# Format: mysql+pymysql://<user>:<password>@<host>:<port>/<db_name>
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 
    'mysql+pymysql://root:password@localhost:3306/farm_db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
init_db(app)

# --- Blueprint Registration ---
# Interface 1 (Farmer / FPO & Core Services)
app.register_blueprint(auth_bp)
app.register_blueprint(farmer_profile_bp)
app.register_blueprint(fpo_profile_bp)
app.register_blueprint(listings_bp)
app.register_blueprint(orders_bp)
app.register_blueprint(analytics_bp)
app.register_blueprint(utils_bp)

# Interface 2 (Consumer & Bulk Buyer)
app.register_blueprint(buyer_auth_bp)
app.register_blueprint(buyer_portal_bp)

# Interface 3 (Pickup & Delivery / Driver)
app.register_blueprint(driver_auth_bp)
app.register_blueprint(driver_portal_bp)

# Interface 4 (Admin & Platform Governance)
app.register_blueprint(admin_auth_bp)
app.register_blueprint(admin_portal_bp)

def format_response(status, data=None, message=""):
    return jsonify({"status": status, "data": data, "message": message})

@app.errorhandler(404)
def not_found(error):
    return format_response("error", message="Requested endpoint or resource not found"), 404

@app.errorhandler(500)
def server_error(error):
    return format_response("error", message="Internal server error occurred"), 500

@app.route('/')
def home():
    return format_response("success", message="Farm Platform Master API (All 4 Interfaces) is operational!")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
