import os
import random
import time
from datetime import datetime, timezone, timedelta
from flask import Flask, render_template, jsonify, request
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Clés de sécurité respectives
ACCESS_CODE_LUCKY = "SDYAHV2517"
ACCESS_CODE_MINES = "WDYAHV2500"
ACCESS_CODE_TRADING = "TRAG679DGA"

# Routes de navigation
@app.route('/')
@app.route('/hub')
def hub_page():
    return render_template('hub.html')

@app.route('/lucky')
def lucky_page():
    return render_template('lucky.html')

@app.route('/mines')
def mines_page():
    return render_template('mines.html')

@app.route('/trading')
def trading_page():
    return render_template('trading.html')

# API - Lucky Jet
@app.route('/api/predict-lucky', methods=['POST'])
def predict_lucky():
    data = request.get_json() or {}
    user_code = data.get('access_code', '')

    if user_code != ACCESS_CODE_LUCKY:
        return jsonify({"status": "error", "message": "ACCESS DENIED: INVALID SECURITY KEY"}), 403

    current_timestamp = int(time.time())
    time_window = current_timestamp // 20
    random.seed(time_window)
    
    rand = random.random()
    if rand < 0.70:
        predicted_odds = round(random.uniform(1.85, 6.50), 2)
    else:
        predicted_odds = round(random.uniform(6.50, 32.40), 2)
        
    confidence = random.randint(89, 99)
    time_plus_45s = datetime.now(timezone.utc) + timedelta(seconds=45)
    current_time_ci = time_plus_45s.strftime("%H:%M:%S")
    
    return jsonify({
        "status": "success",
        "predicted_odds": predicted_odds,
        "confidence": f"{confidence}%",
        "timestamp": current_time_ci
    })

# API - Mines VIP
@app.route('/api/predict-mines', methods=['POST'])
def predict_mines():
    data = request.get_json() or {}
    user_code = data.get('access_code', '')
    
    try:
        mines_count = int(data.get('mines_count', 3))
        if mines_count not in [1, 3, 5, 7]:
            mines_count = 3
    except ValueError:
        mines_count = 3

    if user_code != ACCESS_CODE_MINES:
        return jsonify({"status": "error", "message": "ACCESS DENIED: INVALID SECURITY KEY"}), 403

    current_timestamp = int(time.time())
    random.seed(current_timestamp)
    
    if mines_count == 1:
        stars_to_reveal = random.randint(5, 8)
    elif mines_count == 3:
        stars_to_reveal = random.randint(4, 6)
    elif mines_count == 5:
        stars_to_reveal = random.randint(3, 5)
    elif mines_count == 7:
        stars_to_reveal = random.randint(2, 4)
    else:
        stars_to_reveal = random.randint(3, 5)

    all_cells = list(range(25))
    safe_cells_count = 25 - mines_count
    actual_stars_count = min(stars_to_reveal, safe_cells_count)
    
    predicted_stars = random.sample(all_cells, actual_stars_count)
    confidence = random.randint(95, 99)
    current_time_gmt = datetime.now(timezone.utc).strftime("%H:%M:%S")
    
    return jsonify({
        "status": "success",
        "predicted_stars": predicted_stars,
        "confidence": f"{confidence}%",
        "timestamp": current_time_gmt
    })

# API - Trading VIP
@app.route('/api/signal', methods=['POST'])
def generate_signal():
    data = request.get_json() or {}
    user_code = data.get('access_code', '').strip().upper()

    if user_code != ACCESS_CODE_TRADING:
        return jsonify({'error': 'Code d\'accès invalide'}), 401

    asset = data.get('asset', 'EUR/USD (OTC)')
    timeframe = data.get('timeframe', '30s')

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
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)