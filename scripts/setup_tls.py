import subprocess
import os
import shutil
import sys
import argparse
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def generate_server_cert(force=False):
    """
    Génère un certificat TLS pour le serveur avec SAN pour 127.0.0.1.
    Si 'force' est True, il régénère même si un certificat existe déjà.
    """
    server_cert_dir = os.path.join(os.path.dirname(__file__), '..', 'server', 'certs')
    os.makedirs(server_cert_dir, exist_ok=True)
    cert_path = os.path.join(server_cert_dir, 'server.crt')
    key_path = os.path.join(server_cert_dir, 'server.key')
    if not force and os.path.exists(cert_path) and os.path.exists(key_path):
        logger.info("✅ Certificat serveur déjà existant.")
        return cert_path, key_path
    logger.info("🔄 Génération d'un nouveau certificat TLS avec extension SAN...")
    subj = "/C=FR/ST=Ile-de-France/L=Paris/O=TP/OU=Server/CN=127.0.0.1"
    command = [
        "openssl", "req", "-new", "-x509", "-days", "365",
        "-nodes", "-out", cert_path, "-keyout", key_path,
        "-subj", subj,
        "-addext", "subjectAltName = IP:127.0.0.1"
    ]
    try:
        subprocess.run(command, check=True)
        logger.info("✅ Certificat serveur généré avec succès.")
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Erreur lors de la génération du certificat serveur : {e}")
        sys.exit(1)
    return cert_path, key_path

def setup_client_ca(cert_path, force=False):
    """
    Configure le client pour qu'il reconnaisse le certificat du serveur en copiant
    le certificat du serveur dans le dossier client sous le nom ca.crt.
    Si 'force' est True, il écrase le fichier existant.
    """
    client_cert_dir = os.path.join(os.path.dirname(__file__), '..', 'client', 'certs')
    os.makedirs(client_cert_dir, exist_ok=True)
    ca_cert_path = os.path.join(client_cert_dir, 'ca.crt')
    if not force and os.path.exists(ca_cert_path):
        logger.info("✅ Certificat CA pour le client déjà configuré.")
        return ca_cert_path
    try:
        shutil.copy(cert_path, ca_cert_path)
        logger.info("✅ Certificat CA pour le client configuré avec succès.")
    except Exception as e:
        logger.error(f"❌ Erreur lors de la configuration du certificat CA pour le client : {e}")
        sys.exit(1)
    return ca_cert_path

def main():
    parser = argparse.ArgumentParser(description="Setup TLS pour le serveur et le client.")
    parser.add_argument("--force", action="store_true", help="Forcer la régénération des certificats.")
    args = parser.parse_args()
    server_cert_path, _ = generate_server_cert(force=args.force)
    setup_client_ca(server_cert_path, force=args.force)

if __name__ == '__main__':
    main()
