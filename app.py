# app.py : Notre serveur principal
import sqlite3
import hashlib # Pour sécuriser le mot de passe
from flask import Flask, request, jsonify, session, render_template

# --- INITIALISATION DE L'APPLICATION ---
app = Flask(__name__)
# Clé secrète pour gérer les sessions (garder l'admin connecté)
app.secret_key = 'une_cle_secrete_tres_difficile_a_deviner'

DATABASE_FILE = 'salle_hexagone.db'

# --- FONCTION POUR SE CONNECTER À LA BDD ---
def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# --- LES ROUTES DE NOTRE APPLICATION (LES URLS) ---

# 1. La page principale : servir votre fichier HTML
@app.route('/')
def index():
    # On dit à Flask de charger et d'afficher votre fichier HTML
    return render_template('index.html')

# 2. API pour récupérer les dates réservées
@app.route('/api/get_dates', methods=['GET'])
def get_dates():
    conn = get_db_connection()
    dates_db = conn.execute('SELECT date FROM reservations').fetchall()
    conn.close()
    # On transforme la liste des dates en un format simple [ "2024-12-25", "2024-12-31" ]
    reserved_dates = [row['date'] for row in dates_db]
    return jsonify(reserved_dates)

# 3. API pour la connexion de l'administrateur
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # On "hache" le mot de passe pour le comparer à celui dans la BDD
    password_hash = hashlib.sha256(password.encode()).hexdigest()

    conn = get_db_connection()
    admin = conn.execute('SELECT * FROM admin WHERE username = ? AND password_hash = ?',
                         (username, password_hash)).fetchone()
    conn.close()

    if admin:
        session['is_admin'] = True # On enregistre dans la session que l'admin est connecté
        return jsonify({'success': True, 'message': 'Connexion réussie !'})
    else:
        return jsonify({'success': False, 'message': 'Identifiant ou mot de passe incorrect.'}), 401

# 4. API pour mettre à jour une date (réserver ou annuler)
@app.route('/api/update_date', methods=['POST'])
def update_date():
    # On vérifie si l'utilisateur est bien l'admin connecté
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Accès non autorisé.'}), 403

    data = request.get_json()
    date_str = data.get('date')
    action = data.get('action') # "reserve" ou "cancel"

    conn = get_db_connection()
    if action == 'reserve':
        # On vérifie que la date n'est pas déjà réservée pour éviter les doublons
        existing = conn.execute('SELECT id FROM reservations WHERE date = ?', (date_str,)).fetchone()
        if not existing:
            conn.execute('INSERT INTO reservations (date) VALUES (?)', (date_str,))
    elif action == 'cancel':
        conn.execute('DELETE FROM reservations WHERE date = ?', (date_str,))

    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Date mise à jour.'})

# --- DÉMARRAGE DU SERVEUR ---
if __name__ == '__main__':
    app.run(debug=True) # debug=True pour voir les erreurs facilement pendant le développement