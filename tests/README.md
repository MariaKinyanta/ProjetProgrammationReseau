---
# 🧪 Tests du Projet

Ce dossier contient les tests unitaires et d'intégration permettant de vérifier le bon fonctionnement des modules du projet.

---

## 📌 Contenu des tests

| 📂 Fichier              | 📝 Description                                                         |
|-------------------------|------------------------------------------------------------------------|
| **test_server.py**      | Vérifie les fonctionnalités côté serveur : base de données, authentification, opérations bancaires. |
| **test_client.py**      | Vérifie que le client peut envoyer des requêtes au serveur et recevoir des réponses correctes. |
| **test_security.py**    | Vérifie l’implémentation de la sécurité TLS côté client et serveur.     |

---

## ⚙️ Exécution des tests

### 1. Exécuter tous les tests

Dans le dossier racine du projet, exécutez :

```bash
python -m unittest discover tests

