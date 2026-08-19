import os
import random
import time
from datetime import datetime, timezone, timedelta
from flask import Flask, render_template, jsonify, request
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Nouveaux codes de sécurité distincts pour chaque jeu
CODES = {
    "crash": "CRASH-X99-VIP-26",
    "lucky": "LUCKY-JET-V26-PRO",
    "mines": "MINES-MATRIX-26-X",
    "aviator": "AVIA-SKY-26-VIP"
}

# --- Routes de navigation ---
@app.route('/')
@app.route('/hub')
def hub_page():
    return render_template('hub.html')

# --- Route passerelle intermédiaire (Gateway) ---
@app.route('/game/<game_name>')
def game_gateway(game_name):
    games_info = {
        'crash': {'title': 'Crash', 'provider': '1win Games', 'image': 'crash.png', 'target': '/crash'},
        'lucky': {'title': 'Lucky Jet', 'provider': '1win Games', 'image': 'lucky.png', 'target': '/lucky'},
        'mines': {'title': 'Mines Classic', 'provider': '1win Games', 'image': 'mines.png', 'target': '/mines'},
        'aviator': {'title': 'Aviator', 'provider': 'Spribe', 'image': 'aviator.png', 'target': '/aviator'}
    }
    
    info = games_info.get(game_name, games_info['aviator'])
    return render_template('gateway.html', game=info)

# --- Pages finales des jeux ---
@app.route('/crash')
def crash_page(): return render_template('crash.html')

@app.route('/lucky')
def lucky_page(): return render_template('lucky.html')

@app.route('/mines')
def mines_page(): return render_template('mines.html')

@app.route('/aviator')
def aviator_page(): return render_template('aviator.html')

# --- API : Crash ---
@app.route('/api/predict-crash', methods=['POST'])
def predict_crash():
    data = request.get_json() or {}
    if data.get('access_code') != CODES["crash"]: 
        return jsonify({"error": "Accès refusé"}), 403
    return jsonify({
        "multiplier": f"{round(random.uniform(1.01, 20.00), 2)}x", 
        "confidence": "96%", 
        "timestamp": datetime.now(timezone.utc).strftime("%H:%M:%S")
    })

# --- API : Lucky Jet ---
@app.route('/api/predict-lucky', methods=['POST'])
def predict_lucky():
    data = request.get_json() or {}
    if data.get('access_code') != CODES["lucky"]: 
        return jsonify({"error": "Accès refusé"}), 403
    return jsonify({
        "predicted_odds": round(random.uniform(1.01, 20.00), 2), 
        "confidence": "97%", 
        "timestamp": datetime.now(timezone.utc).strftime("%H:%M:%S")
    })

# --- API : Mines (1, 3, 5, 7 pièges) ---
@app.route('/api/predict', methods=['POST'])
def predict_mines():
    data = request.get_json() or {}
    if data.get('access_code') != CODES["mines"]: 
        return jsonify({"status": "error"}), 403
    
    try:
        mines = int(data.get('mines_count', 3))
        if mines not in [1, 3, 5, 7]: mines = 3
    except ValueError:
        mines = 3

    stars = {1: random.randint(5, 8), 3: random.randint(4, 6), 5: random.randint(3, 5), 7: random.randint(2, 4)}.get(mines, 4)
    return jsonify({
        "status": "success",
        "predicted_stars": random.sample(range(25), min(stars, 25 - mines)), 
        "confidence": "98%", 
        "timestamp": datetime.now(timezone.utc).strftime("%H:%M:%S")
    })

# --- API : Aviator ---
@app.route('/api/predict-aviator', methods=['POST'])
def predict_aviator():
    data = request.get_json() or {}
    if data.get('access_code') != CODES["aviator"]: 
        return jsonify({"error": "Accès refusé"}), 403
    return jsonify({
        "multiplier": f"{round(random.uniform(1.01, 20.00), 2)}x", 
        "confidence": "95%", 
        "timestamp": datetime.now(timezone.utc).strftime("%H:%M:%S")
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)