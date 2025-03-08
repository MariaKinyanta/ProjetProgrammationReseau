from server import auth, db_handler, logger
import csv
import io

log = logger.get_logger(__name__)

def process_client(conn, addr):
    """
    Traite la communication avec un client connecté.
    """
    try:
        data = conn.recv(1024).decode('utf-8').strip()
        log.info(f"Reçu de {addr}: {data}")
        if not data:
            return
        response = handle_request(data)
        log.info(f"Réponse envoyée à {addr}: {response}")
        conn.sendall(response.encode('utf-8'))
    except Exception as e:
        log.error(f"Erreur lors du traitement du client {addr}: {e}")
        try:
            conn.sendall("ERROPERATION".encode('utf-8'))
        except Exception as send_e:
            log.error(f"Erreur lors de l'envoi du message d'erreur à {addr}: {send_e}")

def handle_request(request):
    print("Requête reçue du client:", request)  # Debug
    parts = request.split()
    if len(parts) == 0:
        return "ERROPERATION"
    command = parts[0].upper()

    if command == "TESTPIN":
        if len(parts) != 3:
            return "ERROPERATION"
        account_number, pin = parts[1], parts[2]
        result = auth.verify_pin(account_number, pin)
        if result == "BLOCKED":
            return "COMPTE BLOQUE"
        elif result:
            client_name = db_handler.get_client_name(account_number)
            return f"SESSION_OK {account_number} {client_name}"
        else:
            return "TESTPIN NOK"

    elif command == "GETNAME":
        if len(parts) != 2:
            return "ERROPERATION"
        account_number = parts[1]
        name = db_handler.get_client_name(account_number)
        return f"NAME {name}"

    elif command == "REGISTER":
        # Commande attendue : REGISTER <PIN> <Nom> <Prenom> <Adresse> <CodePostal> <Ville> <TelephoneFixe> <TelephonePortable> <TypeCompte>
        if len(parts) < 9:
            return "ERROPERATION"
        pin = parts[1]
        nom = parts[2]
        prenom = parts[3]
        adresse = parts[4]
        code_postal = parts[5]
        ville = parts[6]
        tel_fixe = parts[7]
        if len(parts) == 9:
            tel_portable = ""
            type_compte = parts[8]
        else:
            tel_portable = parts[8]
            type_compte = " ".join(parts[9:])
        print("Requête REGISTER reçue:", request)  # Debug
        success, result = db_handler.create_account(pin, nom, prenom, adresse, code_postal, ville, tel_fixe, tel_portable, type_compte)
        if success:
            return f"REGISTER OK {result}"
        else:
            return f"REGISTER NOK : {result}"

    elif command == "RETRAIT":
        if len(parts) != 3:
            return "ERROPERATION"
        account_number, amount = parts[1], float(parts[2])
        if db_handler.retirer(account_number, amount):
            db_handler.enregistrer_operation(account_number, "RETRAIT", -amount)
            return "RETRAIT OK"
        return "RETRAIT NOK"

    elif command == "DEPOT":
        if len(parts) != 3:
            return "ERROPERATION"
        account_number, amount = parts[1], float(parts[2])
        if db_handler.deposer(account_number, amount):
            db_handler.enregistrer_operation(account_number, "DEPOT", amount)
            return "DEPOT OK"
        return "DEPOT NOK"

    elif command == "TRANSFERT":
        if len(parts) != 5:
            return "ERROPERATION"
        source, destination, amount_str, pin = parts[1], parts[2], parts[3], parts[4]
        try:
            amount = float(amount_str)
        except ValueError:
            return "ERROPERATION"
        if not db_handler.account_exists(destination):
            return "DESTINATION NON EXISTANTE"
        stored_pin = db_handler.get_pin_for_account(source)
        if stored_pin != pin:
            return "TRANSFERT NOK : PIN invalide"
        if db_handler.transferer(source, destination, amount):
            db_handler.enregistrer_operation(source, "TRANSFERT SORTANT", -amount)
            db_handler.enregistrer_operation(destination, "TRANSFERT ENTRANT", amount)
            dest_name = db_handler.get_client_name(destination)
            return f"TRANSFERT OK : Transfert de {amount} € réussi vers {dest_name} (compte {destination})"
        return "TRANSFERT NOK : montant insuffisant"

    elif command == "SOLDE":
        if len(parts) != 2:
            return "ERROPERATION"
        account_number = parts[1]
        solde = db_handler.get_solde(account_number)
        return f"SOLDE {solde}" if solde is not None else "ERROPERATION"

    elif command == "HISTORIQUE":
        if len(parts) != 2:
            return "ERROPERATION"
        account_number = parts[1]
        operations = db_handler.get_historique(account_number)
        if not operations:
            return "AUCUNE OPERATION"
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Date", "Libellé", "Montant"])
        writer.writerows(operations)
        return output.getvalue()

    else:
        return "ERROPERATION"
