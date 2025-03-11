import unittest
import sqlite3
import os
from server import db_handler, socket_handler

class TestServerCommands(unittest.TestCase):
    def setUp(self):
        # Création d'une base de données temporaire pour les tests
        self.test_db_path = os.path.join(os.path.dirname(__file__), 'test_banque.db')
        conn = sqlite3.connect(self.test_db_path)
        cur = conn.cursor()
        # Création d'une table comptes simplifiée pour les tests
        cur.execute('''
            CREATE TABLE IF NOT EXISTS comptes (
                NumeroCompte TEXT PRIMARY KEY,
                PIN TEXT,
                Solde REAL
            )
        ''')
        # Table opérations pour enregistrer les transactions
        cur.execute('''
            CREATE TABLE IF NOT EXISTS operations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                NumeroCompte TEXT,
                date TEXT,
                libelle TEXT,
                montant REAL
            )
        ''')
        # Insertion de deux comptes de test
        cur.execute("INSERT INTO comptes (NumeroCompte, PIN, Solde) VALUES ('123456', '0000', 500.0)")
        cur.execute("INSERT INTO comptes (NumeroCompte, PIN, Solde) VALUES ('654321', '1111', 300.0)")
        conn.commit()
        conn.close()
        # Rediriger la base utilisée par db_handler vers la base de test
        db_handler.DB_PATH = self.test_db_path

    def tearDown(self):
        os.remove(self.test_db_path)

    def test_retrait_succes(self):
        response = socket_handler.handle_request("RETRAIT 123456 100")
        self.assertEqual(response, "RETRAIT OK")
        self.assertEqual(db_handler.get_solde("123456"), 400.0)

    def test_retrait_echec(self):
        response = socket_handler.handle_request("RETRAIT 123456 1000")
        self.assertEqual(response, "RETRAIT NOK")

    def test_depot_succes(self):
        response = socket_handler.handle_request("DEPOT 123456 200")
        self.assertEqual(response, "DEPOT OK")
        self.assertEqual(db_handler.get_solde("123456"), 700.0)

    def test_transfert_succes(self):
        response = socket_handler.handle_request("TRANSFERT 123456 654321 100 0000")
        self.assertTrue(response.startswith("TRANSFERT OK"))
        self.assertEqual(db_handler.get_solde("123456"), 400.0)
        self.assertEqual(db_handler.get_solde("654321"), 400.0)

    def test_solde(self):
        response = socket_handler.handle_request("SOLDE 123456")
        self.assertTrue(response.startswith("SOLDE"))
        self.assertIn("500.0", response)

    def test_historique_vide(self):
        response = socket_handler.handle_request("HISTORIQUE 123456")
        self.assertEqual(response, "AUCUNE OPERATION")

if __name__ == '__main__':
    unittest.main()
