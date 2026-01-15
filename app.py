from flask import Flask, render_template, request, jsonify
import uuid
from datetime import datetime, timedelta

app = Flask(__name__)

# --- CANDY COIN SYSTEM CONFIGURATION ---
TOTAL_SUPPLY = 100000000000  # 100 Billion
MINING_LIMIT = 10000000000   # 10 Billion Stop
DAILY_MINING_REWARD = 2.0    # 2 Coins per 24 hours
MINING_COOLDOWN = 12         # 12 Hours per session
EXCHANGE_FEE = 0.01          # 1% Tax for Admin

# Database Simulation
db_users = {}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    refer_code = data.get('refer_code')

    if email in db_users:
        return jsonify({"status": "error", "message": "Email already registered"})

    # The first user to register becomes the ADMIN
    is_admin = len(db_users) == 0
    user_id = str(uuid.uuid4())[:8].upper()

    db_users[email] = {
        "id": user_id,
        "password": password,
        "balance": 0.0,
        "is_admin": is_admin,
        "last_mine": None,
        "refer_by": refer_code
    }

    # Referral Logic: Referrer gets 1 coin
    if refer_code:
        for user in db_users.values():
            if user['id'] == refer_code:
                user['balance'] += 1.0
                break

    return jsonify({
        "status": "success", 
        "user_id": user_id, 
        "is_admin": is_admin,
        "message": "OTP Sent to Email (Simulated)"
    })

@app.route('/api/mining/start', methods=['POST'])
def start_mining():
    data = request.json
    email = data.get('email')
    user = db_users.get(email)

    if not user:
        return jsonify({"status": "error", "message": "User not found"})

    # Admin Auto-Mining Logic
    if user['is_admin']:
        user['balance'] += 0.05  # Admin gets constant auto-flow
        return jsonify({"status": "success", "balance": f"{user['balance']:.6f}"})

    # Standard User 12-Hour Cooldown Logic
    now = datetime.now()
    if user['last_mine'] and now < user['last_mine'] + timedelta(hours=MINING_COOLDOWN):
        remaining = (user['last_mine'] + timedelta(hours=MINING_COOLDOWN)) - now
        return jsonify({"status": "error", "message": f"Wait {str(remaining).split('.')[0]}"})

    user['balance'] += 1.0  # 1 Coin per 12 hours = 2 Coins per day
    user['last_mine'] = now
    return jsonify({"status": "success", "balance": f"{user['balance']:.6f}"})

@app.route('/api/exchange', methods=['POST'])
def exchange():
    data = request.json
    email = data.get('email')
    user = db_users.get(email)

    if user['balance'] <= 0:
        return jsonify({"status": "error", "message": "Zero balance"})

    # Admin Fee Logic
    if user['is_admin']:
        # Admin pays 0% Fee
        user['balance'] = 0
        return jsonify({"status": "success", "message": "Admin Exchange Free"})
    else:
        # User pays 1% Fee to Admin
        fee = user['balance'] * EXCHANGE_FEE
        user['balance'] = 0
        
        # Send fee to Admin (First User)
        for u in db_users.values():
            if u['is_admin']:
                u['balance'] += fee
                break
                
        return jsonify({"status": "success", "message": f"1% Fee ({fee:.4f}) sent to Admin"})

if __name__ == "__main__":
    app.run(debug=True)
