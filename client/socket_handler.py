import socket
import os
from client import security, logger

log = logger.get_logger(__name__)

SOCKET_TIMEOUT = 5  # secondes

def send_request(request, server_host, server_port, cafile):
    """
    Se connecte au serveur, sécurise la connexion avec TLS, envoie la requête
    et retourne la réponse complète lue en boucle.
    """
    log.info(f"Connexion à {server_host}:{server_port}")
    try:
        with socket.create_connection((server_host, server_port), timeout=SOCKET_TIMEOUT) as sock:
            with security.wrap_socket_with_tls(sock, server_hostname=server_host, cafile=cafile) as secure_sock:
                log.info(f"Connexion sécurisée établie avec {server_host}:{server_port}")
                secure_sock.sendall(request.encode('utf-8'))
                chunks = []
                while True:
                    chunk = secure_sock.recv(4096)
                    if not chunk:
                        break
                    chunks.append(chunk)
                response = b"".join(chunks).decode('utf-8')
                log.info(f"Réponse reçue: {response}")
                return response
    except socket.timeout:
        log.error("Timeout : Le serveur ne répond pas.")
        return "ERREUR : TIMEOUT"
    except Exception as e:
        log.error(f"Erreur lors de l'envoi de la requête : {e}")
        return "ERREUR : ÉCHEC DE COMMUNICATION"
