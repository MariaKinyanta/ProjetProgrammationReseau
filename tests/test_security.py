import unittest
from unittest.mock import patch, MagicMock
import ssl
from client import security

class TestClientSecurity(unittest.TestCase):
    @patch('client.security.ssl.create_default_context')
    def test_wrap_socket_with_tls(self, mock_create_default_context):
        # Création d'un contexte SSL factice et d'une socket sécurisée fictive
        fake_context = MagicMock()
        fake_secure_socket = MagicMock()
        fake_context.wrap_socket.return_value = fake_secure_socket
        mock_create_default_context.return_value = fake_context

        import socket
        dummy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = security.wrap_socket_with_tls(dummy_socket, "localhost", "dummy_cafile")

        # Vérifier que create_default_context a bien été appelé et que le cafile se termine par "dummy_cafile"
        mock_create_default_context.assert_called()
        args, kwargs = mock_create_default_context.call_args
        self.assertTrue(kwargs['cafile'].endswith("dummy_cafile"))
        fake_context.wrap_socket.assert_called_with(dummy_socket, server_hostname="localhost")
        self.assertEqual(result, fake_secure_socket)
        dummy_socket.close()

if __name__ == '__main__':
    unittest.main()
