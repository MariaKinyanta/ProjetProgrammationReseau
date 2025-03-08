import sqlite3
import csv
import os

# Chemin de la base de données
db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'banque.db')

# Suppression de l'ancienne base pour tout recommencer proprement
if os.path.exists(db_path):
    os.remove(db_path)

# Connexion à la base SQLite
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# ✅ Création des tables
cursor.executescript("""
CREATE TABLE clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numeroCompte TEXT UNIQUE NOT NULL,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    adresse TEXT,
    telephone TEXT
);

CREATE TABLE comptes (
    numeroCompte TEXT PRIMARY KEY,
    pin TEXT NOT NULL,
    solde REAL NOT NULL,
    client_id INTEGER,
    FOREIGN KEY (client_id) REFERENCES clients(id)
);

CREATE TABLE operations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numeroCompte TEXT NOT NULL,
    date TEXT NOT NULL,
    libelle TEXT NOT NULL,
    montant REAL NOT NULL,
    FOREIGN KEY (numeroCompte) REFERENCES comptes(numeroCompte)
);
""")

print("✅ Tables créées avec succès.")

# 📌 Fonction pour importer un fichier CSV
def import_csv(file_path, query, mapping_func):
    if not os.path.exists(file_path):
        print(f"❌ Fichier introuvable : {file_path}")
        return 0
    with open(file_path, 'r', encoding='utf8') as file:
        reader = csv.DictReader(file, delimiter=';', quotechar='"')
        rows = [mapping_func(row) for row in reader]
        cursor.executemany(query, rows)
        conn.commit()
        print(f"✅ {len(rows)} enregistrements importés depuis {file_path}")
        return len(rows)

# ✅ Import des clients
import_csv(
    os.path.join(os.path.dirname(__file__), '..', 'data', 'clients.csv'),
    "INSERT OR IGNORE INTO clients (numeroCompte, nom, prenom, adresse, telephone) VALUES (?, ?, ?, ?, ?)",
    lambda row: (row['NumeroClient'].strip(), row['Nom'].strip(), row['Prenom'].strip(), row['Adresse'].strip(), row['TelephonePortable'].strip())
)

# ✅ Import des comptes
import_csv(
    os.path.join(os.path.dirname(__file__), '..', 'data', 'comptes.csv'),
    "INSERT OR IGNORE INTO comptes (numeroCompte, pin, solde, client_id) VALUES (?, ?, ?, ?)",
    lambda row: (row['NumeroCompte'].strip(), row['PIN'].strip(), float(row['Solde'].replace(',', '.')), row['NumeroClient'].strip())
)

# ✅ Import des opérations
import_csv(
    os.path.join(os.path.dirname(__file__), '..', 'data', 'operations.csv'),
    "INSERT OR IGNORE INTO operations (numeroCompte, date, libelle, montant) VALUES (?, ?, ?, ?)",
    lambda row: (row['NumeroCompte'].strip(), row['DateOperation'].strip(), row['LibelleOperation'].strip(), float(row['Montant'].replace(',', '.')))
)

# Fermeture de la connexion
conn.close()
print("✅ Base de données initialisée avec succès.")
