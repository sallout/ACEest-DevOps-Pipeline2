from flask import Flask, jsonify, request
import os

app = Flask(__name__)

# In-memory store representing the database for cloud-native statelessness
clients = []

programs = {
    "Fat Loss (FL)": {"factor": 22, "desc": "3-day full-body fat loss"},
    "Muscle Gain (MG)": {"factor": 35, "desc": "Push/Pull/Legs hypertrophy"},
    "Beginner (BG)": {"factor": 26, "desc": "3-day simple beginner full-body"}
}

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint for Kubernetes probes."""
    return jsonify({
        "status": "healthy",
        "message": "ACEest Fitness API v1.0 running",
        "version": os.getenv("APP_VERSION", "1.0.0")
    }), 200

@app.route('/programs', methods=['GET'])
def get_programs():
    """Retrieve available fitness programs."""
    return jsonify({"status": "success", "data": programs}), 200

@app.route('/clients', methods=['POST'])
def register_client():
    """Register a new gym client."""
    data = request.get_json()
    
    if not data or 'name' not in data or 'program' not in data:
        return jsonify({"status": "error", "message": "Name and program are required"}), 400
        
    name = data['name']
    program = data['program']
    weight = data.get('weight', 0)
    
    if program not in programs:
        return jsonify({"status": "error", "message": "Invalid program selected"}), 400
        
    calories = int(weight * programs[program]['factor']) if weight > 0 else 0
    
    new_client = {
        "id": len(clients) + 1,
        "name": name,
        "program": program,
        "weight": weight,
        "target_calories": calories
    }
    
    clients.append(new_client)
    return jsonify({"status": "success", "data": new_client}), 201

@app.route('/clients', methods=['GET'])
def get_clients():
    """Retrieve all registered clients."""
    return jsonify({"status": "success", "data": clients}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)