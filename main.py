from flask import Flask, jsonify
from database import init_db

app = Flask(__name__)
app.secret_key = 'super_secret_farm_key'

# Initialize Database
init_db(app)

# Helper function for unified responses
def format_response(status, data=None, message=""):
    return jsonify({"status": status, "data": data, "message": message})

# Error Handlers
@app.errorhandler(404)
def not_found(error):
    return format_response("error", message="Resource not found"), 404

@app.errorhandler(500)
def server_error(error):
    return format_response("error", message="Internal server error"), 500

@app.route('/')
def home():
    return format_response("success", message="Farm Platform API is running!")

if __name__ == '__main__':
    app.run(debug=True)
