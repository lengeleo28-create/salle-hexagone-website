# setup_database.py : à n'exécuter qu'une seule fois !
import sqlite3
import hashlib

DATABASE_FILE = 'salle_hexagone.db'

# --- VOS IDENTIFIANTS ADMIN ---
ADMIN_USERNAME = "Ruddy"
ADMIN_PASSWORD = "2018" # <-- CHANGEZ CECI !
# -----------------------------

# Hachage du mot de passe pour la sécurité
password_hash = hashlib.sha256(ADMIN_PASSWORD.encode()).hexdigest()

# Connexion et création des tables
conn = sqlite3.connect(DATABASE_FILE)
cursor = conn.cursor()

# Table pour les dates de réservation
cursor.execute('''
    CREATE TABLE IF NOT EXISTS reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL UNIQUE
    )
''')
print("Table 'reservations' créée ou déjà existante.")

# Table pour l'administrateur
cursor.execute('''
    CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL
    )
''')
print("Table 'admin' créée ou déjà existante.")

# On insère l'admin s'il n'existe pas
try:
    cursor.execute("INSERT INTO admin (username, password_hash) VALUES (?, ?)", (ADMIN_USERNAME, password_hash))
    print(f"Utilisateur admin '{ADMIN_USERNAME}' créé avec succès.")
except sqlite3.IntegrityError:
    print(f"L'utilisateur admin '{ADMIN_USERNAME}' existe déjà.")


conn.commit()
conn.close()
print("\nBase de données prête !")