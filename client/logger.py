import logging
import logging.config
import json
import os

def get_logger(name):
    # Chemin vers le fichier de configuration des logs client
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'logging_config_client.json')
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config_dict = json.load(f)
            # Obtenir le répertoire racine du projet et ajuster le chemin du log en absolu
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            if 'handlers' in config_dict and 'file' in config_dict['handlers']:
                rel_path = config_dict['handlers']['file'].get('filename', '')
                abs_log_path = os.path.join(project_root, rel_path)
                config_dict['handlers']['file']['filename'] = abs_log_path
            logging.config.dictConfig(config_dict)
        except Exception as e:
            logging.basicConfig(level=logging.DEBUG)
            logging.getLogger(name).error(f"Erreur chargement logs client: {e}")
    else:
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger(name).error("Fichier de configuration client introuvable.")
    return logging.getLogger(name)
