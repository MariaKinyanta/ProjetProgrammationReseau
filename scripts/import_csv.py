import sqlite3
import csv
import os

# Chemin de la base de données
db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'banque.db')

# Connexion à la base SQLite
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

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

# ✅ Import des opérations uniquement
import_csv(
    os.path.join(os.path.dirname(__file__), '..', 'data', 'operations.csv'),
    "INSERT OR IGNORE INTO operations (numeroCompte, date, libelle, montant) VALUES (?, ?, ?, ?)",
    lambda row: (row['NumeroCompte'].strip(), row['DateOperation'].strip(), row['LibelleOperation'].strip(), float(row['Montant'].replace(',', '.')))
)

# Fermeture de la connexion
conn.close()
print("✅ Importation des opérations terminée avec succès.")
