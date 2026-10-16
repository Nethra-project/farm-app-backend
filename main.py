from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from auth_routes import auth_bp

app = Flask(__name__)
CORS(app)

app.config["JWT_SECRET_KEY"] = "krishibazaar-jwt-secret-key"
jwt = JWTManager(app)

app.register_blueprint(auth_bp)

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "success", "message": "Krishi Bazaar API Server is running!"}), 200

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
