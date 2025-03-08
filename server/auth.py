from server import db_handler, logger
import time

log = logger.get_logger(__name__)

FAILED_ATTEMPTS = {}
SESSIONS = {}

MAX_ATTEMPTS = 3
BLOCK_DURATION = 300  # 5 minutes

def verify_pin(account_number, pin):
    current_time = time.time()

    if account_number in FAILED_ATTEMPTS:
        attempts, block_until = FAILED_ATTEMPTS[account_number]
        if block_until and current_time < block_until:
            log.warning(f"Compte {account_number} verrouillé jusqu'à {time.ctime(block_until)}")
            return "BLOCKED"

    try:
        stored_pin = db_handler.get_pin_for_account(account_number)
        if stored_pin is None:
            log.warning(f"Compte {account_number} non trouvé ou PIN manquant.")
            return False

        stored_pin_str = str(stored_pin).strip()
        provided_pin_str = str(pin).strip()

        log.info(f"Comparaison pour compte {account_number}: PIN stocké='{stored_pin_str}' | PIN fourni='{provided_pin_str}'")

        if stored_pin_str == provided_pin_str:
            log.info(f"Authentification réussie pour le compte {account_number}")
            session_id = f"SESSION_{account_number}_{int(current_time)}"
            SESSIONS[account_number] = session_id
            FAILED_ATTEMPTS.pop(account_number, None)
            return session_id
        else:
            log.info(f"Authentification échouée pour le compte {account_number}")
            attempts, _ = FAILED_ATTEMPTS.get(account_number, (0, None))
            attempts += 1
            block_until = None
            if attempts >= MAX_ATTEMPTS:
                block_until = current_time + BLOCK_DURATION
                log.warning(f"Compte {account_number} bloqué pour {BLOCK_DURATION} secondes")
            FAILED_ATTEMPTS[account_number] = (attempts, block_until)
            return False
    except Exception as e:
        log.error(f"Erreur lors de la vérification du PIN pour le compte {account_number}: {e}")
        return False

def end_session(account_number):
    if account_number in SESSIONS:
        del SESSIONS[account_number]
        log.info(f"Session du compte {account_number} terminée.")
        return True
    return False

def is_session_active(account_number):
    return account_number in SESSIONS

