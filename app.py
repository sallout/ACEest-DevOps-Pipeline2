import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)
DB_NAME = "aceest_fitness.db"

def init_db():
    """Initialize the SQLite database mirroring Aceestver-3.2.4.py schema."""
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        
        # Users (for role-based login)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT,
                role TEXT
            )
        """)
        
        # Clients
        cur.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                age INTEGER,
                height REAL,
                weight REAL,
                program TEXT,
                calories INTEGER,
                target_weight REAL,
                target_adherence INTEGER,
                membership_status TEXT,
                membership_end TEXT
            )
        """)
        
        # Add default admin if not exists
        cur.execute("SELECT * FROM users WHERE username='admin'")
        if not cur.fetchone():
            cur.execute("INSERT INTO users VALUES ('admin','admin','Admin')")
        
        conn.commit()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Kubernetes readiness probes."""
    return jsonify({"status": "healthy"}), 200

@app.route('/api/login', methods=['POST'])
def login():
    """Authenticate user based on users table."""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("SELECT role FROM users WHERE username=? AND password=?", (username, password))
        row = cur.fetchone()
        
    if row:
        return jsonify({"message": "Login successful", "role": row[0]}), 200
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/api/clients', methods=['GET', 'POST'])
def handle_clients():
    """Retrieve all clients or create a new client."""
    if request.method == 'GET':
        with sqlite3.connect(DB_NAME) as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, name, program, membership_status FROM clients")
            clients = [{"id": r[0], "name": r[1], "program": r[2], "status": r[3]} for r in cur.fetchall()]
        return jsonify(clients), 200

    if request.method == 'POST':
        data = request.get_json()
        name = data.get('name')
        if not name:
            return jsonify({"error": "Name is required"}), 400
            
        try:
            with sqlite3.connect(DB_NAME) as conn:
                cur = conn.cursor()
                cur.execute("INSERT INTO clients (name, membership_status) VALUES (?, ?)", (name, "Active"))
                conn.commit()
            return jsonify({"message": f"Client {name} created"}), 201
        except sqlite3.IntegrityError:
            return jsonify({"error": "Client already exists"}), 409

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)