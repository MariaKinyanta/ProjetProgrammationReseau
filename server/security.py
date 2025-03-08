import ssl
from server import logger

log = logger.get_logger(__name__)

def wrap_socket_with_tls(sock, certfile, keyfile):
    """
    Enveloppe la socket avec TLS pour le serveur.
    Charge le certificat et la clé privée, puis enveloppe la socket en mode serveur.
    """
    try:
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile=certfile, keyfile=keyfile)
        secure_sock = context.wrap_socket(sock, server_side=True)
        log.info("Socket sécurisée avec TLS.")
        return secure_sock
    except ssl.SSLError as e:
        log.error(f"Erreur lors de l'enveloppement TLS: {e}")
        raise
