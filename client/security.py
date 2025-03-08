import ssl
import os
from client import logger

log = logger.get_logger(__name__)

def wrap_socket_with_tls(sock, server_hostname, cafile):
    """
    Enveloppe la socket avec TLS en vérifiant strictement le certificat du serveur.
    """
    # Conversion du chemin relatif en chemin absolu
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    abs_cafile = os.path.join(project_root, cafile)
    log.info(f"Utilisation du fichier CA : {abs_cafile}")

    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=abs_cafile)
    context.check_hostname = True        # Vérifie que le nom du serveur correspond
    context.verify_mode = ssl.CERT_REQUIRED  # Exige un certificat valide

    try:
        secure_sock = context.wrap_socket(sock, server_hostname=server_hostname)
        log.info("Connexion sécurisée avec TLS établie.")
        return secure_sock
    except ssl.SSLError as e:
        log.error(f"Erreur SSL : {e}")
        raise
