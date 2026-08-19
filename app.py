import os
import random
import time
from datetime import datetime, timezone
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Code d'accès VIP
ACCESS_CODE = "TRAG679DGA"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/signal', methods=['POST'])
def generate_signal():
    data = request.get_json() or {}
    user_code = data.get('access_code', '').strip().upper()

    if user_code != ACCESS_CODE:
        return jsonify({'error': 'Code d\'accès invalide'}), 401

    asset = data.get('asset', 'EUR/USD (OTC)')
    timeframe = data.get('timeframe', '30s')

    # Simulation d'analyse algorithmique
    time.sleep(random.uniform(0.6, 1.2))

    direction = random.choice(['HAUT (CALL) 📈', 'BAS (PUT) 📉'])
    confidence = f"{random.randint(88, 98)}%"
    timestamp = datetime.now(timezone.utc).strftime("%H:%M:%S")

    return jsonify({
        'asset': asset,
        'timeframe': timeframe,
        'direction': direction,
        'confidence': confidence,
        'timestamp': timestamp,
        'status': 'success'
    })

if __name__ == '__main__':
    # Configuration du port dynamique requis pour le déploiement
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)