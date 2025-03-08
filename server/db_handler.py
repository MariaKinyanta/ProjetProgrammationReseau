import sqlite3
import os
from server import logger

log = logger.get_logger(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'banque.db')

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_pin_for_account(account_number):
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT pin FROM comptes WHERE numeroCompte = ?", (account_number,))
            row = cur.fetchone()
            return row["pin"] if row else None
    except Exception as e:
        log.error(f"Erreur lors de l'accès au PIN pour le compte {account_number}: {e}")
        return None

def get_solde(account_number):
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT solde FROM comptes WHERE numeroCompte = ?", (account_number,))
            row = cur.fetchone()
            return row["solde"] if row else None
    except Exception as e:
        log.error(f"Erreur lors de la récupération du solde: {e}")
        return None

def account_exists(account_number):
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM comptes WHERE numeroCompte = ?", (account_number,))
            row = cur.fetchone()
            return row is not None
    except Exception as e:
        log.error(f"Erreur lors de la vérification de l'existence du compte {account_number}: {e}")
        return False

def retirer(account_number, amount):
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT solde FROM comptes WHERE numeroCompte = ?", (account_number,))
            row = cur.fetchone()
            if row and row["solde"] >= amount:
                new_balance = row["solde"] - amount
                cur.execute("UPDATE comptes SET solde = ? WHERE numeroCompte = ?", (new_balance, account_number))
                conn.commit()
                return True
            return False
    except Exception as e:
        log.error(f"Erreur lors du retrait pour le compte {account_number}: {e}")
        return False

def deposer(account_number, amount):
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("UPDATE comptes SET solde = solde + ? WHERE numeroCompte = ?", (amount, account_number))
            conn.commit()
            return True
    except Exception as e:
        log.error(f"Erreur lors du dépôt pour le compte {account_number}: {e}")
        return False

def transferer(source_account, destination_account, amount):
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT solde FROM comptes WHERE numeroCompte = ?", (source_account,))
            source_solde = cur.fetchone()
            if not source_solde or source_solde["solde"] < amount:
                return False
            cur.execute("UPDATE comptes SET solde = solde - ? WHERE numeroCompte = ?", (amount, source_account))
            cur.execute("UPDATE comptes SET solde = solde + ? WHERE numeroCompte = ?", (amount, destination_account))
            conn.commit()
            return True
    except Exception as e:
        log.error(f"Erreur lors du transfert de {source_account} vers {destination_account}: {e}")
        return False

def enregistrer_operation(account_number, libelle, montant):
    try:
        from datetime import datetime
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO operations (numeroCompte, date, libelle, montant)
                VALUES (?, ?, ?, ?)
            """, (account_number, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), libelle, montant))
            conn.commit()
    except Exception as e:
        log.error(f"Erreur lors de l'enregistrement de l'opération pour le compte {account_number}: {e}")

def get_historique(account_number):
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT date, libelle, montant
                FROM operations
                WHERE numeroCompte = ?
                ORDER BY date DESC
                LIMIT 10
            """, (account_number,))
            rows = cur.fetchall()
            return [(row["date"], row["libelle"], row["montant"]) for row in rows]
    except Exception as e:
        log.error(f"Erreur lors de la récupération de l'historique pour le compte {account_number}: {e}")
        return []

def get_client_name(account_number):
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            # Jointure via la clé étrangère client_id (clients.id)
            cur.execute("""
                SELECT c.prenom, c.nom
                FROM clients c
                JOIN comptes co ON c.id = co.client_id
                WHERE co.numeroCompte = ?
            """, (account_number,))
            row = cur.fetchone()
            if row:
                return f"{row['prenom']} {row['nom']}"
            else:
                return "Inconnu"
    except Exception as e:
        log.error(f"Erreur lors de la récupération du nom pour le compte {account_number}: {e}")
        return "Inconnu"

def generate_new_account_number():
    """
    Génère un nouveau numéro de compte en incrémentant le maximum existant.
    On suppose que les numéros de compte sont stockés sous forme numérique.
    """
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT MAX(CAST(numeroCompte AS INTEGER)) AS max_num FROM comptes")
            row = cur.fetchone()
            if row and row["max_num"] is not None:
                new_number = int(row["max_num"]) + 1
            else:
                new_number = 1000000000  # Démarrage à un grand nombre pour éviter les conflits
            return str(new_number)
    except Exception as e:
        log.error(f"Erreur lors de la génération du nouveau numéro de compte: {e}")
        return None

def create_account(pin, nom, prenom, adresse, code_postal, ville, tel_fixe, tel_portable, type_compte):
    """
    Pour créer un compte, on utilise les données suivantes :
      - Dans la table clients, on stocke :
          • numeroCompte : généré (et utilisé comme identifiant de compte)
          • nom, prenom, adresse
          • telephone : on utilisera le téléphone portable (cf. import CSV)
      - Dans la table comptes, on insère :
          • numeroCompte identique
          • pin et solde (0.0)
          • client_id : l'ID auto-généré dans clients
    Les autres champs (codePostal, ville, tel_fixe, type_compte) ne sont pas stockés dans ce schéma.
    """
    print(f"Tentative de création de compte avec PIN={pin}, Nom={nom}, Prénom={prenom}, Adresse={adresse}, CP={code_postal}, Ville={ville}, Tél fixe={tel_fixe}, Tél portable={tel_portable}, Type={type_compte}")  # Debug
    try:
        new_account = generate_new_account_number()
        if not new_account:
            return False, "Impossible de générer un nouveau numéro de compte"
        with get_connection() as conn:
            cur = conn.cursor()
            # Insertion dans la table clients
            cur.execute("""
                INSERT INTO clients (numeroCompte, nom, prenom, adresse, telephone)
                VALUES (?, ?, ?, ?, ?)
            """, (new_account, nom, prenom, adresse, tel_portable))
            client_id = cur.lastrowid
            # Insertion dans la table comptes
            cur.execute("""
                INSERT INTO comptes (numeroCompte, pin, solde, client_id)
                VALUES (?, ?, ?, ?)
            """, (new_account, pin, 0.0, client_id))
            conn.commit()
            return True, new_account
    except Exception as e:
        log.error(f"Erreur lors de la création du compte: {e}")
        return False, f"Erreur lors de la création du compte: {e}"
