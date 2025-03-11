import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
from tkinter import ttk
from ttkthemes import ThemedTk
from client import socket_handler, logger
import time
import os
import csv
import io

# Configuration des logs
log = logger.get_logger(__name__)

# Paramètres serveur
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5001
CAFILE = "client/certs/ca.crt"

class BankClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Client Bancaire - Banque d'Excellence")
        # Autorise le redimensionnement horizontal/vertical
        self.root.resizable(True, True)
        self.root.geometry("900x600")
        self.root.minsize(300, 250)
        self.session_active = False
        self.account_number = None
        self.client_name = ""
        self.user_pin = None

        self.create_menu()

        # Configuration du thème et du style
        self.style = ttk.Style(self.root)
        self.root.set_theme("plastik")
        navy = "#002147"
        bleu_moyen = "#003366"
        dore = "#D4AF37"

        self.style.configure("TFrame", background=navy)
        self.style.configure("TLabel", background=navy, foreground="white", font=("Segoe UI", 12))
        self.style.configure("Header.TLabel", background=navy, foreground=dore, font=("Segoe UI", 16, "bold"))
        self.style.configure("TButton", font=("Segoe UI", 12, "bold"), padding=6,
                             background=dore, foreground=navy, borderwidth=0)
        self.style.map("TButton", background=[("active", "#b7950b"), ("!active", dore)])
        self.style.configure("Treeview", background="white", foreground=navy, fieldbackground="white", font=("Segoe UI", 11))
        self.style.configure("Treeview.Heading", background=dore, foreground=navy, font=("Segoe UI", 12, "bold"))
        self.style.configure("Login.TFrame", background=bleu_moyen, relief="flat")
        self.style.configure("Login.TLabel", background=bleu_moyen, foreground="white", font=("Segoe UI", 12))
        self.style.configure("Login.TEntry", font=("Segoe UI", 12))

        # Configuration pour rendre la fenêtre responsive
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.create_login_screen()

    def create_menu(self):
        menubar = tk.Menu(self.root, background="#001c33", foreground="white", activebackground="#001933")
        self.root.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0, background="#001c33", foreground="white", activebackground="#001933")
        menubar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Nouvelle instance", command=self.open_new_instance)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.root.quit)

    def open_new_instance(self):
        new_window = ThemedTk(theme="plastik")
        new_window.title("Nouvelle instance - Client Bancaire")
        BankClientApp(new_window)
        new_window.mainloop()

    def create_login_screen(self):
        self.clear_screen()
        login_frame = ttk.Frame(self.root, style="Login.TFrame", padding="30")
        login_frame.grid(row=0, column=0, sticky="nsew")

        # Rendre le cadre responsive
        login_frame.grid_rowconfigure(0, weight=0)
        login_frame.grid_rowconfigure(1, weight=0)
        login_frame.grid_rowconfigure(2, weight=0)
        login_frame.grid_rowconfigure(3, weight=0)
        login_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(login_frame, text="Numéro de compte:", style="Login.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 10))
        self.account_entry = ttk.Entry(login_frame, font=("Segoe UI", 12))
        self.account_entry.grid(row=0, column=1, sticky="ew", pady=(0, 10))

        ttk.Label(login_frame, text="PIN:", style="Login.TLabel").grid(row=1, column=0, sticky="w", pady=(0, 10))
        self.pin_entry = ttk.Entry(login_frame, font=("Segoe UI", 12), show="*")
        self.pin_entry.grid(row=1, column=1, sticky="ew", pady=(0, 10))

        login_btn = ttk.Button(login_frame, text="Se Connecter", command=self.authenticate)
        login_btn.grid(row=2, column=0, columnspan=2, pady=20)

        reg_btn = ttk.Button(login_frame, text="Créer un compte", command=self.create_registration_screen)
        reg_btn.grid(row=3, column=0, columnspan=2, pady=10)

    def create_registration_screen(self):
        self.clear_screen()
        reg_frame = ttk.Frame(self.root, style="Login.TFrame", padding="30")
        reg_frame.grid(row=0, column=0, sticky="nsew")

        reg_frame.grid_rowconfigure(list(range(12)), weight=0)
        reg_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(reg_frame, text="Inscription", style="Header.TLabel").grid(row=0, column=0, columnspan=2, pady=(0, 20))

        ttk.Label(reg_frame, text="PIN:", style="Login.TLabel").grid(row=1, column=0, sticky="w", pady=5)
        pin_entry = ttk.Entry(reg_frame, font=("Segoe UI", 12), show="*")
        pin_entry.grid(row=1, column=1, sticky="ew", pady=5)

        ttk.Label(reg_frame, text="Nom:", style="Login.TLabel").grid(row=2, column=0, sticky="w", pady=5)
        nom_entry = ttk.Entry(reg_frame, font=("Segoe UI", 12))
        nom_entry.grid(row=2, column=1, sticky="ew", pady=5)

        ttk.Label(reg_frame, text="Prénom:", style="Login.TLabel").grid(row=3, column=0, sticky="w", pady=5)
        prenom_entry = ttk.Entry(reg_frame, font=("Segoe UI", 12))
        prenom_entry.grid(row=3, column=1, sticky="ew", pady=5)

        ttk.Label(reg_frame, text="Adresse:", style="Login.TLabel").grid(row=4, column=0, sticky="w", pady=5)
        adresse_entry = ttk.Entry(reg_frame, font=("Segoe UI", 12))
        adresse_entry.grid(row=4, column=1, sticky="ew", pady=5)

        ttk.Label(reg_frame, text="Code Postal:", style="Login.TLabel").grid(row=5, column=0, sticky="w", pady=5)
        cp_entry = ttk.Entry(reg_frame, font=("Segoe UI", 12))
        cp_entry.grid(row=5, column=1, sticky="ew", pady=5)

        ttk.Label(reg_frame, text="Ville:", style="Login.TLabel").grid(row=6, column=0, sticky="w", pady=5)
        ville_entry = ttk.Entry(reg_frame, font=("Segoe UI", 12))
        ville_entry.grid(row=6, column=1, sticky="ew", pady=5)

        ttk.Label(reg_frame, text="Téléphone Fixe:", style="Login.TLabel").grid(row=7, column=0, sticky="w", pady=5)
        tel_fixe_entry = ttk.Entry(reg_frame, font=("Segoe UI", 12))
        tel_fixe_entry.grid(row=7, column=1, sticky="ew", pady=5)

        ttk.Label(reg_frame, text="Téléphone Portable:", style="Login.TLabel").grid(row=8, column=0, sticky="w", pady=5)
        tel_portable_entry = ttk.Entry(reg_frame, font=("Segoe UI", 12))
        tel_portable_entry.grid(row=8, column=1, sticky="ew", pady=5)

        ttk.Label(reg_frame, text="Type de Compte:", style="Login.TLabel").grid(row=9, column=0, sticky="w", pady=5)
        type_compte_combo = ttk.Combobox(reg_frame, font=("Segoe UI", 12), state="readonly")
        type_compte_combo['values'] = (
            "Compte courant",
            "Livret d'épargne",
            "Plan épargne logement",
            "Plan épargne bancaire",
            "Assurance vie"
        )
        type_compte_combo.current(0)
        type_compte_combo.grid(row=9, column=1, sticky="ew", pady=5)

        reg_btn = ttk.Button(
            reg_frame,
            text="Créer le compte",
            command=lambda: self.register_user(
                pin_entry.get().strip(),
                nom_entry.get().strip(),
                prenom_entry.get().strip(),
                adresse_entry.get().strip(),
                cp_entry.get().strip(),
                ville_entry.get().strip(),
                tel_fixe_entry.get().strip(),
                tel_portable_entry.get().strip(),
                type_compte_combo.get().strip()
            )
        )
        reg_btn.grid(row=10, column=0, columnspan=2, pady=20)

        retour_btn = ttk.Button(reg_frame, text="Retour au Login", command=self.create_login_screen)
        retour_btn.grid(row=11, column=0, columnspan=2, pady=10)

    def register_user(self, pin, nom, prenom, adresse, cp, ville, tel_fixe, tel_portable, type_compte):
        if not pin or not nom or not prenom:
            messagebox.showerror("Erreur", "Les champs 'PIN', 'Nom' et 'Prénom' sont obligatoires.")
            return
        command = f"REGISTER {pin} {nom} {prenom} {adresse} {cp} {ville} {tel_fixe} {tel_portable} {type_compte}"
        log.info("Commande envoyée au serveur: %s", command)
        response = socket_handler.send_request(command, SERVER_HOST, SERVER_PORT, CAFILE)
        log.info("Réponse du serveur: %s", response)
        if response and response.startswith("REGISTER OK"):
            parts = response.split()
            new_account = parts[2] if len(parts) >= 3 else "Inconnu"
            messagebox.showinfo("Succès", f"Compte créé avec succès.\nVotre numéro de compte est {new_account}.\nVeuillez vous connecter.")
            self.create_login_screen()
        else:
            messagebox.showerror("Erreur", f"Erreur lors de la création du compte : {response}")

    def create_main_screen(self):
        self.clear_screen()
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, sticky="nsew")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Onglet Accueil
        self.dashboard_tab = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.dashboard_tab, text="Accueil")
        self.dashboard_tab.grid_rowconfigure(2, weight=1)
        self.dashboard_tab.grid_columnconfigure(0, weight=1)

        # Onglet Historique
        self.history_tab = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.history_tab, text="Historique")
        self.history_tab.grid_rowconfigure(0, weight=1)
        self.history_tab.grid_columnconfigure(0, weight=1)

        # ----- Dashboard -----
        header_frame = ttk.Frame(self.dashboard_tab, padding="10")
        header_frame.grid(row=0, column=0, sticky="ew")
        self.info_label = ttk.Label(
            header_frame,
            text=f"Bienvenue, {self.client_name} (compte {self.account_number}) | Solde : N/A",
            style="Header.TLabel"
        )
        self.info_label.pack(anchor="center", pady=10)
        self.update_account_info()

        actions_frame = ttk.Frame(self.dashboard_tab, padding="10")
        actions_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        actions = [
            ("Retrait", self.action_withdraw),
            ("Dépôt", self.action_deposit),
            ("Transfert", self.action_transfer),
            ("Solde", self.action_balance),
            ("Historique", lambda: self.notebook.select(self.history_tab)),
            ("Se Déconnecter", self.logout)
        ]
        for idx, (text, command) in enumerate(actions):
            btn = ttk.Button(actions_frame, text=text, command=command)
            btn.grid(row=0, column=idx, padx=5, sticky="nsew")
            actions_frame.columnconfigure(idx, weight=1)

        log_frame = ttk.Frame(self.dashboard_tab, padding="10")
        log_frame.grid(row=2, column=0, sticky="nsew", pady=(10, 0))
        self.op_tree = ttk.Treeview(log_frame, columns=("Opération", "Message", "Heure"), show="headings")
        self.op_tree.heading("Opération", text="Opération")
        self.op_tree.heading("Message", text="Message")
        self.op_tree.heading("Heure", text="Heure")
        self.op_tree.column("Opération", anchor="w", width=200)
        self.op_tree.column("Message", anchor="w", width=500)
        self.op_tree.column("Heure", anchor="center", width=100)
        self.op_tree.grid(row=0, column=0, sticky="nsew")
        log_frame.grid_rowconfigure(0, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.op_tree.yview)
        self.op_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        # ----- Historique -----
        history_frame = ttk.Frame(self.history_tab, padding="10")
        history_frame.grid(row=0, column=0, sticky="nsew")
        history_frame.grid_rowconfigure(0, weight=1)
        history_frame.grid_columnconfigure(0, weight=1)

        self.history_tree = ttk.Treeview(history_frame, columns=("Date", "Libellé", "Montant"), show="headings")
        self.history_tree.heading("Date", text="Date")
        self.history_tree.heading("Libellé", text="Libellé")
        self.history_tree.heading("Montant", text="Montant")
        self.history_tree.column("Date", anchor="center", width=150)
        self.history_tree.column("Libellé", anchor="center", width=250)
        self.history_tree.column("Montant", anchor="center", width=100)
        self.history_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar2 = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar2.set)
        scrollbar2.grid(row=0, column=1, sticky="ns")

        download_btn = ttk.Button(self.history_tab, text="Télécharger l'historique", command=self.download_history)
        download_btn.grid(row=1, column=0, pady=10)

        self.load_history()
        self.start_auto_refresh()

    def start_auto_refresh(self):
        """
        Rafraîchit automatiquement le solde et l'historique toutes les 10 secondes,
        tant que la session est active.
        """
        if self.session_active:
            self.update_account_info()
            self.load_history()
        self.root.after(10000, self.start_auto_refresh)

    def update_account_info(self):
        response = socket_handler.send_request(f"SOLDE {self.account_number}", SERVER_HOST, SERVER_PORT, CAFILE)
        solde = response.split()[1] if response.startswith("SOLDE") and len(response.split()) > 1 else "N/A"
        info_text = f"Bienvenue, {self.client_name} (compte {self.account_number}) | Solde : {solde} €"
        self.info_label.config(text=info_text)

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def send_request(self, request):
        try:
            response = socket_handler.send_request(request, SERVER_HOST, SERVER_PORT, CAFILE)
            friendly_msg = self.format_operation_message(request, response)
            current_time = time.strftime("%H:%M:%S")
            self.op_tree.insert("", "end", values=(request.split()[0].upper(), friendly_msg, current_time))
            return response
        except Exception as e:
            messagebox.showerror("Erreur", f"Échec de la communication avec le serveur : {e}", parent=self.root)
            return ""

    def format_operation_message(self, request, response):
        parts = request.split()
        cmd = parts[0].upper()
        if cmd == "RETRAIT":
            try:
                amount = float(parts[2])
            except Exception:
                amount = "?"
            return f"Retrait de {amount} € réussi." if response == "RETRAIT OK" else f"Retrait de {amount} € échoué."
        elif cmd == "DEPOT":
            try:
                amount = float(parts[2])
            except Exception:
                amount = "?"
            return f"Dépôt de {amount} € réussi." if response == "DEPOT OK" else f"Dépôt de {amount} € échoué."
        elif cmd == "TRANSFERT":
            return response  # Affichage complet de la réponse pour le transfert
        elif cmd == "SOLDE":
            return response
        elif cmd == "HISTORIQUE":
            return "Historique actualisé."
        else:
            return response

    def authenticate(self):
        self.account_number = self.account_entry.get().strip()
        pin = self.pin_entry.get().strip()
        if not self.account_number or not pin:
            messagebox.showerror("Erreur", "Veuillez saisir le numéro de compte et le PIN", parent=self.root)
            return
        response = socket_handler.send_request(f"TESTPIN {self.account_number} {pin}", SERVER_HOST, SERVER_PORT, CAFILE)
        if response.startswith("SESSION_OK"):
            parts = response.split()
            self.client_name = " ".join(parts[2:]) if len(parts) >= 3 else "Inconnu"
            self.user_pin = pin
            self.session_active = True
            self.create_main_screen()
        else:
            messagebox.showerror("Erreur", "Échec de l'authentification", parent=self.root)

    def action_withdraw(self):
        amount = simpledialog.askfloat("Retrait", "Montant à retirer:", parent=self.root)
        if amount is None:
            return
        confirm_pin = simpledialog.askstring("Confirmation", "Veuillez confirmer votre PIN pour cette opération:", show="*", parent=self.root)
        if confirm_pin is None or confirm_pin != self.user_pin:
            messagebox.showerror("Erreur", "PIN de confirmation invalide.", parent=self.root)
            return
        resp = self.send_request(f"RETRAIT {self.account_number} {amount}")
        messagebox.showinfo("Retrait", resp, parent=self.root)
        self.update_account_info()
        self.load_history()

    def action_deposit(self):
        amount = simpledialog.askfloat("Dépôt", "Montant à déposer:", parent=self.root)
        if amount is None:
            return
        confirm_pin = simpledialog.askstring("Confirmation", "Veuillez confirmer votre PIN pour cette opération:", show="*", parent=self.root)
        if confirm_pin is None or confirm_pin != self.user_pin:
            messagebox.showerror("Erreur", "PIN de confirmation invalide.", parent=self.root)
            return
        resp = self.send_request(f"DEPOT {self.account_number} {amount}")
        messagebox.showinfo("Dépôt", resp, parent=self.root)
        self.update_account_info()
        self.load_history()

    def action_transfer(self):
        dest = simpledialog.askstring("Transfert", "Numéro de compte destinataire:", parent=self.root)
        amount = simpledialog.askfloat("Transfert", "Montant à transférer:", parent=self.root)
        if dest is None or amount is None:
            return
        confirm_pin = simpledialog.askstring("Confirmation", "Veuillez confirmer votre PIN pour cette opération:", show="*", parent=self.root)
        if confirm_pin is None or confirm_pin != self.user_pin:
            messagebox.showerror("Erreur", "PIN de confirmation invalide.", parent=self.root)
            return
        name_response = socket_handler.send_request(f"GETNAME {dest}", SERVER_HOST, SERVER_PORT, CAFILE)
        if name_response.startswith("NAME "):
            _, _, dest_name = name_response.partition(" ")
            dest_name = dest_name.strip()
        else:
            dest_name = "Inconnu"
        confirm = messagebox.askyesno("Confirmation", f"Vous allez envoyer {amount} € à {dest_name} (compte {dest}). Confirmez-vous ?", parent=self.root)
        if not confirm:
            messagebox.showinfo("Annulation", "Transfert annulé.", parent=self.root)
            return
        resp = self.send_request(f"TRANSFERT {self.account_number} {dest} {amount} {self.user_pin}")
        messagebox.showinfo("Transfert", resp, parent=self.root)
        self.update_account_info()
        self.load_history()

    def action_balance(self):
        resp = self.send_request(f"SOLDE {self.account_number}")
        messagebox.showinfo("Solde", resp, parent=self.root)
        self.update_account_info()

    def load_history(self):
        response = socket_handler.send_request(f"HISTORIQUE {self.account_number}", SERVER_HOST, SERVER_PORT, CAFILE)
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        if response.startswith("AUCUNE OPERATION"):
            self.history_tree.insert("", "end", values=("Aucune opération", "", ""))
        else:
            f = io.StringIO(response)
            reader = csv.reader(f)
            headers = next(reader, None)
            for row in reader:
                if len(row) >= 3:
                    self.history_tree.insert("", "end", values=(row[0], row[1], row[2]))
            f.close()

    def download_history(self):
        if not self.account_number:
            messagebox.showerror("Erreur", "Aucun compte connecté.")
            return
        response = socket_handler.send_request(f"HISTORIQUE {self.account_number}", SERVER_HOST, SERVER_PORT, CAFILE)
        if response.startswith("AUCUNE OPERATION"):
            messagebox.showinfo("Téléchargement impossible", "Aucune opération trouvée.")
            return
        download_folder = os.path.join(os.path.dirname(__file__), "Telechargement")
        os.makedirs(download_folder, exist_ok=True)
        base_filename = f"historique_{self.account_number}"
        file_path = os.path.join(download_folder, f"{base_filename}.csv")
        counter = 1
        while os.path.exists(file_path):
            file_path = os.path.join(download_folder, f"{base_filename}_{counter}.csv")
            counter += 1
        try:
            with open(file_path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                reader = csv.reader(io.StringIO(response))
                writer.writerows(reader)
            messagebox.showinfo("Téléchargement réussi", f"L'historique a été enregistré dans :\n{file_path}", parent=self.root)
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement du fichier : {e}", parent=self.root)

    def logout(self):
        socket_handler.send_request("DECONNECTER", SERVER_HOST, SERVER_PORT, CAFILE)
        self.session_active = False
        self.create_login_screen()

if __name__ == '__main__':
    root = ThemedTk(theme="plastik")
    app = BankClientApp(root)
    root.mainloop()
