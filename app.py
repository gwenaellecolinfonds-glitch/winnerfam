import os
import random
import time
import json
import requests
from datetime import datetime, timezone, timedelta
from flask import Flask, render_template, jsonify, request
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# --- CONFIGURATION TELEGRAM ---
TELEGRAM_BOT_TOKEN = "8378796687:AAF-hCn6Tt8oh7VsMliQdGG-69HJRTF3sRk"
TELEGRAM_CHAT_ID = "7782921218"

# Fichier pour sauvegarder durablement les ID acceptés (pour qu'ils ne s'effacent pas au redémarrage)
DB_FILE = "approved_users.json"

def load_database():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_database(data):
    try:
        with open(DB_FILE, "w") as f:
            json.dump(data, f)
    except Exception as e:
        print("Erreur sauvegarde DB:", e)

# Base de données chargée en mémoire
PLAYER_STATUS = load_database()

def send_telegram_approval_request(player_id, game_name):
    if not TELEGRAM_BOT_TOKEN:
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    inline_keyboard = {
        "inline_keyboard": [
            [
                {"text": "✅ Accepter", "callback_data": f"approve_{player_id}"},
                {"text": "❌ Refuser", "callback_data": f"reject_{player_id}"}
            ]
        ]
    }
    
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": (
            f"⏳ *NOUVELLE DEMANDE D'ACCÈS VIP* ⏳\n\n"
            f"🆔 *ID 1win unique :* `{player_id}`\n"
            f"🎮 *Jeu ciblé :* {game_name}\n"
            f"🎟️ *Code requis :* `GODWIN5`\n\n"
            f"👇 *Choisissez une action :*"
        ),
        "parse_mode": "Markdown",
        "reply_markup": inline_keyboard
    }
    
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print("Erreur Telegram:", e)

# --- Routes de navigation ---
@app.route('/')
@app.route('/hub')
def hub_page():
    return render_template('hub.html')

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

@app.route('/crash')
def crash_page(): return render_template('crash.html')

@app.route('/lucky')
def lucky_page(): return render_template('lucky.html')

@app.route('/mines')
def mines_page(): return render_template('mines.html')

@app.route('/aviator')
def aviator_page(): return render_template('aviator.html')

# --- GESTION DES ACCÈS VIP (ID UNIQUE) ---

@app.route('/api/submit-player-id', methods=['POST'])
def submit_player_id():
    data = request.get_json() or {}
    player_id = data.get('player_id', '').strip()
    game_name = data.get('game', 'Inconnu').upper()
    
    if not player_id or len(player_id) < 4:
        return jsonify({"status": "error", "message": "ID 1win invalide"}), 400
    
    # Vérifie si l'ID est déjà approuvé définitivement
    if PLAYER_STATUS.get(player_id) == "approved":
        return jsonify({"status": "approved", "message": "Accès autorisé"})
    
    # Si l'ID n'est pas encore approuvé et qu'il n'est pas déjà en attente
    if player_id not in PLAYER_STATUS or PLAYER_STATUS[player_id] == "rejected":
        PLAYER_STATUS[player_id] = "pending"
        save_database(PLAYER_STATUS)
        send_telegram_approval_request(player_id, game_name)
    
    status = PLAYER_STATUS[player_id]
    if status == "approved":
        return jsonify({"status": "approved", "message": "Accès autorisé"})
    elif status == "rejected":
        return jsonify({"status": "rejected", "message": "Accès refusé par l'administrateur."})
    else:
        return jsonify({"status": "pending", "message": "En attente de validation."})

@app.route('/api/check-status', methods=['POST'])
def check_status():
    data = request.get_json() or {}
    player_id = data.get('player_id', '').strip()
    status = PLAYER_STATUS.get(player_id, "pending")
    return jsonify({"status": status})

# ⚡ WEBHOOK TELEGRAM : Gère l'acceptation définitive d'un ID unique
@app.route('/telegram-webhook', methods=['POST'])
def telegram_webhook():
    data = request.get_json() or {}
    
    if "callback_query" in data:
        callback = data["callback_query"]
        callback_data = callback["data"]
        chat_id = callback["message"]["chat"]["id"]
        message_id = callback["message"]["message_id"]
        
        if callback_data.startswith("approve_"):
            player_id = callback_data.replace("approve_", "")
            PLAYER_STATUS[player_id] = "approved"
            save_database(PLAYER_STATUS)  # Sauvegarde permanente
            new_text = f"✅ *ID UNIQUE {player_id} ACCEPTÉ ✅*\nCet utilisateur a maintenant un accès permanent aux jeux."
        elif callback_data.startswith("reject_"):
            player_id = callback_data.replace("reject_", "")
            PLAYER_STATUS[player_id] = "rejected"
            save_database(PLAYER_STATUS)
            new_text = f"❌ *ID UNIQUE {player_id} REFUSÉ ❌*\nL'accès a été bloqué."
        else:
            return jsonify({"status": "ok"})
        
        edit_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/editMessageText"
        requests.post(edit_url, json={
            "chat_id": chat_id,
            "message_id": message_id,
            "text": new_text,
            "parse_mode": "Markdown"
        })
        
        answer_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery"
        requests.post(answer_url, json={"callback_query_id": callback["id"], "text": "Enregistré avec succès !"})
        
    return jsonify({"status": "ok"})

# --- FONCTION UTILITAIRE : Heure cible du round (+35 secondes) ---
def get_target_play_time():
    target = datetime.now(timezone.utc) + timedelta(seconds=35)
    return target.strftime("%H:%M:%S")

# --- API : Jeux ---
@app.route('/api/predict-crash', methods=['POST'])
def predict_crash():
    time.sleep(0.8)
    multiplier = round(random.uniform(1.01, 10.00), 2)
    return jsonify({"multiplier": f"{multiplier}x", "confidence": "96%", "target_time": get_target_play_time()})

@app.route('/api/predict-lucky', methods=['POST'])
def predict_lucky():
    time.sleep(0.8)
    predicted_odds = round(random.uniform(1.01, 10.00), 2)
    return jsonify({"predicted_odds": predicted_odds, "confidence": "97%", "target_time": get_target_play_time()})

@app.route('/api/predict', methods=['POST'])
def predict_mines():
    data = request.get_json() or {}
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
        "target_time": get_target_play_time()
    })

@app.route('/api/predict-aviator', methods=['POST'])
def predict_aviator():
    time.sleep(0.8)
    fly_multiplier = round(random.uniform(1.01, 10.00), 2)
    return jsonify({"multiplier": f"{fly_multiplier}x", "confidence": "95%", "target_time": get_target_play_time()})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)