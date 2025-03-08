import socket
import ssl
import threading
import json
import os
import signal
import sys
from server import socket_handler, security, logger

log = logger.get_logger(__name__)

# Chargement de la configuration du serveur
CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'server_config.json')
with open(CONFIG_PATH, 'r') as f:
    config = json.load(f)

HOST = config.get("host", "0.0.0.0")
PORT = config.get("port", 5001)
CERTFILE = os.path.join(os.path.dirname(__file__), '..', config.get("certfile", "server/certs/server.crt"))
KEYFILE = os.path.join(os.path.dirname(__file__), '..', config.get("keyfile", "server/certs/server.key"))

def handle_client(conn, addr):
    log.info(f"Connexion établie depuis {addr}")
    try:
        socket_handler.process_client(conn, addr)
    except Exception as e:
        log.error(f"Erreur lors du traitement du client {addr}: {e}")
    finally:
        conn.close()
        log.info(f"Connexion fermée pour {addr}")

def shutdown_server(signal_received, frame):
    log.info("Arrêt du serveur demandé. Fermeture des connexions...")
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, shutdown_server)

    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile=CERTFILE, keyfile=KEYFILE)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((HOST, PORT))
        sock.listen(5)
        log.info(f"Serveur à l'écoute sur {HOST}:{PORT}")

        while True:
            client_sock, addr = sock.accept()
            try:
                conn = context.wrap_socket(client_sock, server_side=True)
            except ssl.SSLError as e:
                log.error(f"Erreur SSL avec {addr}: {e}")
                client_sock.close()
                continue
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.daemon = True
            client_thread.start()

if __name__ == '__main__':
    main()
