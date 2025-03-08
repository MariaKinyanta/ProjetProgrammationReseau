
---

# 🏦 Projet Final - Programmation Réseau (Client-Serveur sécurisé)

Ce projet est réalisé dans le cadre d’un **examen de programmation réseau**. Il implémente un **système bancaire** où des distributeurs automatiques communiquent avec un serveur central via TCP sécurisé avec **TLS**.

## 📌 Fonctionnalités

✅ Vérification du **PIN** avant toute transaction  
✅ **Requêtes bancaires** : Retrait, Dépôt, Virement, Solde, Historique  
✅ **Base de données SQLite3** pour stocker les comptes et opérations  
✅ Communication **sécurisée** avec chiffrement TLS  
✅ **Logs persistants** pour chaque transaction côté client et serveur  
✅ **Tests unitaires** pour valider chaque module

---

## 📂 Arborescence du projet

```
ProjetFinalProgrammationReseau/
├── client/                   # Code du client (simulateur de distributeur automatique)
│   ├── main_client.py        # Lancement du client
│   ├── socket_handler.py     # Communication avec le serveur
│   ├── security.py           # Sécurisation TLS côté client
│   ├── logger.py             # Gestion des logs
│   ├── logs/                 # Dossier contenant les logs du client
│   │   └── client.log        # Fichier de logs des activités du client
│   └── __init__.py           
│
├── server/                   # Code du serveur central bancaire
│   ├── main_server.py        # Lancement du serveur
│   ├── socket_handler.py     # Communication avec les clients
│   ├── db_handler.py         # Gestion de la base de données SQLite3
│   ├── auth.py               # Vérification des PINs et authentification
│   ├── security.py           # Sécurisation TLS côté serveur
│   ├── logger.py             # Gestion des logs
│   ├── logs/                 # Dossier contenant les logs du serveur
│   │   └── server.log        # Fichier de logs des transactions serveur
│   └── __init__.py           
│
├── scripts/                  # Scripts utiles pour préparer l’environnement
│   ├── create_db.py          # Création de la base de données
│   ├── import_csv.py         # Import des fichiers CSV dans la base
│   ├── setup_tls.py          # Génération des certificats TLS
│
├── config/                   # Fichiers de configuration
│   ├── server_config.json    # Configuration du serveur
│   ├── client_config.json    # Configuration du client
│   ├── logging_config.json   # Configuration des logs serveur
│   ├── logging_config_client.json # Configuration des logs client
│
├── data/                     # Données de test
│   ├── banque.db             # Base de données SQLite3
│   ├── clients.csv           # Liste des clients
│   ├── comptes.csv           # Informations des comptes
│   ├── operations.csv        # Historique des transactions
│
├── tests/                    # Tests unitaires et d'intégration
│   ├── test_server.py        # Tests côté serveur
│   ├── test_client.py        # Tests côté client
│   ├── test_security.py      # Tests de sécurité TLS
│   ├── README.md             # Documentation des tests
│
└── README.md                 # Documentation principale du projet
```

---

## ⚙️ Installation et Configuration

### 🔹 1. Installer Python
Assurez-vous d’avoir **Python 3.6+** installé sur votre machine.

### 🔹 2. Installer les dépendances
Dans le dossier du projet, exécutez :
```bash
pip install -r requirements.txt
```
_(Ajoutez un fichier `requirements.txt` si nécessaire, contenant `sqlite3` et `ssl`)_

### 🔹 3. Créer la base de données
Exécutez :
```bash
python scripts/create_db.py
```

### 🔹 4. Importer les données des fichiers CSV
```bash
python scripts/import_csv.py
```

### 🔹 5. Générer les certificats TLS
```bash
python scripts/setup_tls.py
```

---

## 🚀 Exécution du projet

### 🖥️ Démarrer le **serveur**
```bash
python server/main_server.py
```

### 🏧 Démarrer un **client**
```bash
python client/main_client.py
```

---

## 🧪 Tests et Debugging

### 🔹 Exécuter les tests unitaires
```bash
python -m unittest discover tests
```

### 🔹 Avec `pytest` (optionnel)
```bash
pytest
```

### 📜 Logs
- Les logs du serveur sont dans **server/logs/server.log**
- Les logs du client sont dans **client/logs/client.log**

---

## 📌 Remarques

⚠️ Ce projet est **un examen universitaire**, il n’est **pas prévu pour une utilisation en production**.  
✅ Il est conçu pour illustrer la **programmation réseau sécurisée** en Python.  
💡 Vous pouvez le modifier pour tester d’autres types d’attaques et renforcer la sécurité.

---

## 👨‍💻 Auteur

📌 **Nom** : *KINYANTA WA KINYANTA MARIA*  
📌 **Université** : *NOUVEAUX HORIZONS*

---

# ProjetProgrammationReseau
