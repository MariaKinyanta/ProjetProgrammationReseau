import unittest
from unittest.mock import patch, MagicMock
from client import socket_handler

class TestClientCommands(unittest.TestCase):
    @patch('client.socket_handler.security.wrap_socket_with_tls')
    @patch('client.socket_handler.socket.socket')
    def test_retrait(self, mock_socket_class, mock_wrap_socket):
        mock_sock = MagicMock()
        mock_secure_sock = MagicMock()
        # Simuler la réception en deux étapes : le message puis la fin (chunk vide)
        mock_secure_sock.recv.side_effect = ["RETRAIT OK".encode("utf-8"), b""]
        mock_socket_class.return_value = mock_sock
        mock_wrap_socket.return_value = mock_secure_sock

        response = socket_handler.send_request("RETRAIT 123456 100", "127.0.0.1", 5001, "dummy_cafile")
        self.assertEqual(response, "RETRAIT OK")

    @patch('client.socket_handler.security.wrap_socket_with_tls')
    @patch('client.socket_handler.socket.socket')
    def test_depot(self, mock_socket_class, mock_wrap_socket):
        mock_sock = MagicMock()
        mock_secure_sock = MagicMock()
        mock_secure_sock.recv.side_effect = ["DEPOT OK".encode("utf-8"), b""]
        mock_socket_class.return_value = mock_sock
        mock_wrap_socket.return_value = mock_secure_sock

        response = socket_handler.send_request("DEPOT 123456 200", "127.0.0.1", 5001, "dummy_cafile")
        self.assertEqual(response, "DEPOT OK")

    @patch('client.socket_handler.security.wrap_socket_with_tls')
    @patch('client.socket_handler.socket.socket')
    def test_transfert(self, mock_socket_class, mock_wrap_socket):
        mock_sock = MagicMock()
        mock_secure_sock = MagicMock()
        expected_response = "TRANSFERT OK : Transfert de 100.0 € réussi vers Inconnu (compte 654321)"
        mock_secure_sock.recv.side_effect = [expected_response.encode("utf-8"), b""]
        mock_socket_class.return_value = mock_sock
        mock_wrap_socket.return_value = mock_secure_sock

        response = socket_handler.send_request("TRANSFERT 123456 654321 100 0000", "127.0.0.1", 5001, "dummy_cafile")
        self.assertTrue(response.startswith("TRANSFERT OK"))

    @patch('client.socket_handler.security.wrap_socket_with_tls')
    @patch('client.socket_handler.socket.socket')
    def test_solde(self, mock_socket_class, mock_wrap_socket):
        mock_sock = MagicMock()
        mock_secure_sock = MagicMock()
        mock_secure_sock.recv.side_effect = ["SOLDE 500.0".encode("utf-8"), b""]
        mock_socket_class.return_value = mock_sock
        mock_wrap_socket.return_value = mock_secure_sock

        response = socket_handler.send_request("SOLDE 123456", "127.0.0.1", 5001, "dummy_cafile")
        self.assertEqual(response, "SOLDE 500.0")

    @patch('client.socket_handler.security.wrap_socket_with_tls')
    @patch('client.socket_handler.socket.socket')
    def test_historique(self, mock_socket_class, mock_wrap_socket):
        mock_sock = MagicMock()
        mock_secure_sock = MagicMock()
        csv_response = "Date,Libellé,Montant\n2025-02-20,DEPOT,100.0\n2025-02-21,RETRAIT,-50.0"
        mock_secure_sock.recv.side_effect = [csv_response.encode("utf-8"), b""]
        mock_socket_class.return_value = mock_sock
        mock_wrap_socket.return_value = mock_secure_sock

        response = socket_handler.send_request("HISTORIQUE 123456", "127.0.0.1", 5001, "dummy_cafile")
        self.assertIn("DEPOT", response)
        self.assertIn("RETRAIT", response)

if __name__ == '__main__':
    unittest.main()
