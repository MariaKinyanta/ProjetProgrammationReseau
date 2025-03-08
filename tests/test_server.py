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

        # Création des tables nécessaires
        cur.execute('''
            CREATE TABLE IF NOT EXISTS comptes (
                numeroCompte TEXT PRIMARY KEY, 
                pin TEXT, 
                solde REAL
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS operations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numeroCompte TEXT,
                date TEXT,
                libelle TEXT,
                montant REAL
            )
        ''')

        # Insertion de comptes de test
        cur.execute("INSERT INTO comptes (numeroCompte, pin, solde) VALUES ('123456', '0000', 500.0)")
        cur.execute("INSERT INTO comptes (numeroCompte, pin, solde) VALUES ('654321', '1111', 300.0)")
        conn.commit()
        conn.close()

        # Redirection de db_handler vers la base de test
        db_handler.DB_PATH = self.test_db_path

    def tearDown(self):
        os.remove(self.test_db_path)

    def test_retrait_succes(self):
        response = socket_handler.handle_request("RETRAIT 123456 100")
        self.assertEqual(response, "RETRAIT OK")
        self.assertEqual(db_handler.get_solde("123456"), 400.0)

    def test_retrait_echec_fonds_insuffisants(self):
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

    def test_transfert_echec_solde_insuffisant(self):
        response = socket_handler.handle_request("TRANSFERT 123456 654321 1000 0000")
        self.assertTrue(response.startswith("TRANSFERT NOK"))

    def test_solde_succes(self):
        response = socket_handler.handle_request("SOLDE 123456")
        self.assertTrue(response.startswith("SOLDE"))
        self.assertIn("500.0", response)

    def test_solde_inconnu(self):
        response = socket_handler.handle_request("SOLDE 000000")
        self.assertEqual(response, "ERROPERATION")

    def test_historique_vide(self):
        response = socket_handler.handle_request("HISTORIQUE 123456")
        self.assertEqual(response, "AUCUNE OPERATION")

    def test_historique_avec_operations(self):
        db_handler.enregistrer_operation("123456", "DEPOT", 100)
        db_handler.enregistrer_operation("123456", "RETRAIT", -50)
        response = socket_handler.handle_request("HISTORIQUE 123456")
        self.assertIn("DEPOT", response)
        self.assertIn("RETRAIT", response)

if __name__ == '__main__':
    unittest.main()
