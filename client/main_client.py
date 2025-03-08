import json
import os
from client import socket_handler, logger

log = logger.get_logger(__name__)

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'client_config.json')

def main():
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
    except Exception as e:
        log.error(f"Erreur lors du chargement de la configuration: {e}")
        return

    server_host = config.get("server_host", "127.0.0.1")
    server_port = config.get("server_port", 5001)
    cafile = os.path.join(os.path.dirname(__file__), '..', config.get("cafile", "client/certs/ca.crt"))

    request = "TESTPIN 123456 0000"
    log.info(f"Envoi de la requête: {request}")

    try:
        response = socket_handler.send_request(request, server_host, server_port, cafile)
        print("Réponse du serveur:", response)
    except Exception as e:
        log.error(f"Erreur lors de l'envoi de la requête: {e}")

if __name__ == '__main__':
    main()
