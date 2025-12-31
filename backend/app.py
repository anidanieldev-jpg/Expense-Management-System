from flask import Flask, jsonify
from flask_cors import CORS
from routes import vendors, wallets, expenses, payments, deposits, sync

app = Flask(__name__)
# Allow CORS for Frontend running on Port 8000 or 8080
CORS(app, resources={r"/v1/*": {"origins": ["http://localhost:8000", "http://localhost:8080"]}})

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "message": "Backend is running. Please access the Frontend at http://localhost:8000"
    })

# Register Blueprints
app.register_blueprint(vendors.bp)
app.register_blueprint(wallets.bp)
app.register_blueprint(expenses.bp)
app.register_blueprint(payments.bp)
app.register_blueprint(deposits.bp)
app.register_blueprint(sync.bp)

# Global Error Handler
@app.errorhandler(404)
def not_found(e):
    return jsonify({"code": 404, "message": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"code": 500, "message": "Internal Server Error"}), 500

if __name__ == '__main__':
    print("Starting Modular Flask API on port 3000...")
    app.run(port=3000, debug=True)
