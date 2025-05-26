from tkinter import *
from tkinter import ttk
import mysql.connector
from tkinter import simpledialog
from tkcalendar import DateEntry
import mysql.connector as msqlc
from datetime import datetime
import serial
import time

# Définir les variables globales pour les Entry widgets
name_entry = None
email_entry = None
password_entry = None
confirm_password_entry = None

def on_entry_click(event, entry, default_text):
    if entry.get() == default_text:
        entry.delete(0, END)

def on_focusout(event, entry, default_text):
    if not entry.get():
        entry.insert(0, default_text)

def toggle_password_visibility():
    global is_password_visible
    if is_password_visible:
        mdp_entry.config(show="*")
        is_password_visible =False
    else:
        mdp_entry.config(show="")
        is_password_visible = True

def login():
    global identifiant_entry, mdp_entry, identifiant_label, mdp_label
    
    # Récupérer les valeurs saisies dans les champs email et mot de passe
    email = identifiant_entry.get()
    password = mdp_entry.get()
    
    # Vérifier si les champs sont vides
    if not email:
        # Afficher une indication visuelle pour les champs vides
        identifiant_label.config(text="*", fg="red")
    if not password:
        # Afficher une indication visuelle pour les champs vides
        mdp_label.config(text="*", fg="red")
        return
    
    # Connecter à la base de données
    try:
        connection = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="",
            database="gestion"
        )

        cursor = connection.cursor()

        # Exécuter une requête pour récupérer les informations de l'utilisateur à partir de l'email fourni
        sql = "SELECT Nom FROM inscription WHERE Email = %s AND Password = %s"
        cursor.execute(sql, (email, password))
        user = cursor.fetchone()

        if user:
            # L'utilisateur est trouvé dans la base de données, afficher un message de bienvenue
            welcome(user[0])
        else:
            # L'utilisateur n'est pas trouvé dans la base de données, afficher un message d'erreur
            print("Error: Email or password incorrect")

    except mysql.connector.Error as error:
        print("Failed to query MySQL table:", error)

    finally:
        # Fermer la connexion à la base de données
        if connection is not None and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

def on_entry_change(event, label):
    label.config(text="") 
def register_account():
    global name_entry, email_entry, password_entry, confirm_password_entry

    # Get the user input from entry widgets
    name = name_entry.get()
    email = email_entry.get()
    password = password_entry.get()
    confirm_password = confirm_password_entry.get()

    # Perform validation on the input fields
    if not (name and email and password and confirm_password):
        messagebox.showerror("Error", "All fields are required")
        return
    elif password != confirm_password:
        messagebox.showerror("Error", "Passwords do not match")
        return

    # Connect to the database
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="gestion"
        )
        cursor = conn.cursor()

        # Insert user details into the database
        query = "INSERT INTO inscription (Nom, Email, Password) VALUES (%s, %s, %s)"
        cursor.execute(query, (name, email, password))
        conn.commit()

        # Close the database connection
        cursor.close()
        conn.close()

        # Inform the user about successful registration
        messagebox.showinfo("Success", "Registration successful!")
    except mysql.connector.Error as err:
        # Handle database errors
        messagebox.showerror("Database Error", f"Error: {err}")

    # Optionally, you can clear the entry fields after successful registration
    name_entry.delete(0, 'end')
    email_entry.delete(0, 'end')
    password_entry.delete(0, 'end')
    confirm_password_entry.delete(0, 'end')

def welcome(user_name):
    global  date_combobox, tableau, cursor

    # Créer une connexion à la base de données MySQL
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="gestion"  # Assurez-vous de remplacer par le nom de votre base de données
    )
    
    # Créer un curseur pour exécuter des requêtes SQL
    cursor = conn.cursor()

    # Créer un canvas pour afficher le titre et les boutons
    logo = Canvas(root, width=1000, height=750, bg="#008080")
    logo.place(relx=0.5, rely=0.5, anchor=CENTER)
    
    # Afficher le titre "Gestion de présence"
    logo1_title = Label(logo, text="Gestion de présence", font=('arial', 25, 'bold'), bg="#008080", fg="black")
    logo1_title.place(relx=0.5, rely=0.2, anchor=CENTER)
    
    # Créer un widget DateEntry pour sélectionner la date
    date_combobox = DateEntry(root, width=12, background='darkblue', foreground='white', borderwidth=2)
    date_combobox.pack(padx=10, pady=180)
    
    # Bouton pour déclencher l'action liée à la sélection de la date
    btn_commencer = Button(logo, text="Commencer l'appel",command=executer_script)
    btn_commencer.place(relx=0.5, rely=0.3, anchor=CENTER)
  
   
    
    afficher_liste_etudiantes()
    
    def remplir_tableau(selected_date):
        global etudiantes
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="gestion"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT id_finger, Présent, Absent FROM appel WHERE Date = %s", (selected_date,))
        liste_data = cursor.fetchall()
    
        if liste_data:
            for etudiante in liste_data:
                id_finger, present, absent = etudiante
                
                for etudiant in tableau.get_children():
                    
                    if tableau.item(etudiant)['values'][0] == id_finger:
                        tableau.item(etudiant, values=(id_finger, tableau.item(etudiant)['values'][1], tableau.item(etudiant)['values'][2], present, absent))
                        break
        else:
            messagebox.showinfo("Avertissement", "Aucune donnée d'absence disponible pour la date sélectionnée.")
    
        conn.commit()
        cursor.close()
        conn.close()



    def on_date_select(event):
        selected_date = date_combobox.get_date()
        remplir_tableau(selected_date)

    date_combobox.bind("<<DateEntrySelected>>", on_date_select)
  


def afficher_liste_etudiantes():
    global  date_combobox, tableau,etudiantes,id_finger1,nom,prenom
    
   
    
    # Créer une connexion à la base de données MySQL
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="gestion"  # Assurez-vous de remplacer par le nom de votre base de données
    )
    
    # Créer un curseur pour exécuter des requêtes SQL
    cursor = conn.cursor()
    
    # Exécuter une requête pour sélectionner toutes les étudiantes de la table Inscriptions
    cursor.execute("SELECT id_finger, Nom, Prenom FROM Inscriptions")
    
    # Récupérer tous les résultats de la requête
    etudiantes = cursor.fetchall()
    
    # Créer un frame pour afficher le tableau
    frame_tableau = Frame(root, bg="#008080")
    frame_tableau.place(relx=0.5, rely=0.6, anchor=CENTER)
    
    # Créer un tableau pour afficher les étudiantes
    tableau = ttk.Treeview(frame_tableau, columns=("id_finger", "Nom", "Prénom","Présent","Absent"), show="headings")
    tableau.heading("id_finger", text="id_finger")
    tableau.heading("Nom", text="Nom")
    tableau.heading("Prénom", text="Prénom")
    tableau.heading("Absent", text="Absent")
    tableau.heading("Présent", text="Présent")
    tableau.pack(fill="both", expand=True)  # Remplir et étirer dans toutes les directions
    
    
    # Ajouter les données récupérées de la base de données au tableau
    for i, etudiante in enumerate(etudiantes):
        # Limiter le nombre de lignes à 127
        if i < 127:
            tableau.insert("", "end", values=etudiante)
        else:
            break
    
    # Configuration de la couleur de fond des en-têtes de colonne
    tableau.tag_configure("::ttk::treeheading", background="#008080", foreground="white")
    
    # Lier un événement de clic droit à une fonction pour la suppression ou la modification
    tableau.bind("<Button-3>", lambda event: clic_droit(event))

    # Fermer le curseur et la connexion à la base de données
    cursor.close()
    conn.close()
    

def clic_droit(event):
    # Récupérer l'élément sélectionné dans le tableau
    item_id = tableau.identify_row(event.y)
    
    # Afficher un menu contextuel pour la suppression, la modification ou l'ajout
    menu = Menu(root, tearoff=0)
    menu.add_command(label="Supprimer", command=lambda: supprimer_entree(item_id))
    menu.add_command(label="Modifier", command=lambda: modifier_presnce(item_id, event))  # Passer item_id et event
    menu.add_command(label="Ajouter nouvelle etudiante", command=ajouter_nouvelle_ligne)
    menu.add_command(label="Modifier Présence/Absence", command=lambda: modifier_presence_absence(item_id))
    menu.post(event.x_root, event.y_root)

import mysql.connector
from tkinter import messagebox
def executer_script():
    import mysql.connector as msqlc
    from datetime import datetime
    import serial
    import time
    
    # Connexion à la base de données
    try:
        bd = msqlc.connect(
            host="localhost",
            port=3306,
            user="root",
            passwd="",
            database="gestion"
        )
        cursor = bd.cursor()
    except Exception as e:
        print("Erreur de connexion à la base de données :", e)
        exit()
    
    # Définition des requêtes SQL
    query_select = "SELECT * FROM inscriptions WHERE id_finger = %s"
    query_insert = "INSERT INTO inscriptions (id_finger) VALUES (%s)"
    query_select_all = "SELECT id_finger FROM inscriptions"
    query_update_present = "UPDATE appel SET Date = %s, Présent = %s ,Absent=%s WHERE id_finger = %s"
    query_insert_absent = "INSERT INTO appel (id_finger, Date, Présent, Absent) VALUES (%s, %s, %s, %s)"
    
    # Initialisation de la connexion série avec l'Arduino
    port = 'COM8'
    arduino_connection = None
    try:
        arduino_connection = serial.Serial(port, 9600, timeout=1)
        
    except Exception as e:
        print("Problème de connexion série avec l'Arduino :", e)
    
    # Création d'une liste pour stocker les ID détectés
    detected_ids = []
    start_time = time.time()
    print("Sair votre doigt")
    while True:
        if arduino_connection:
        
            data = arduino_connection.readline().strip().decode('utf-8')
            if data.isdigit():
                print(data)
                cursor.execute(query_select, (data,))
                result = cursor.fetchone()
    
                if result:
                    print(data, "est déjà présent dans la base de données.")
                    detected_ids.append(int(data))
                else:
                    # Insérer l'ID dans la base de données
                    cursor.execute(query_insert, (data,))
                    bd.commit()
                    print("L'ID", data, "a été ajouté à la base de données.")
        else:
            print("La connexion à l'Arduino a échoué.")
            break
    
    # Récupération de tous les IDs de la base de données
    cursor.execute(query_select_all)
    all_ids = [row[0] for row in cursor.fetchall()]
    
    # Mise à jour des enregistrements dans la base de données
    now = datetime.now()
    for id_detecte in detected_ids:
        cursor.execute(query_select, (id_detecte,))
        ligne_existante = cursor.fetchone()
        if ligne_existante:
            cursor.execute(query_update_present, (now, "x","" ,id_detecte))
        else:
            cursor.execute(query_insert_absent, (id_detecte, now, "x", ""))
        bd.commit()
    
    # Gestion des ID non détectés
    for id_non_detecte in all_ids:
        if id_non_detecte not in detected_ids:
            cursor.execute(query_select, (id_non_detecte,))
            ligne_existante = cursor.fetchone()
            if ligne_existante:
                cursor.execute(query_insert_absent, (id_non_detecte, now, "", "x"))
            bd.commit()


def ajouter_nouvelle_ligne():
    # Créer une boîte de dialogue pour saisir les nouvelles informations
    fenetre_ajout = Toplevel(root)
    fenetre_ajout.title("Ajouter une nouvelle ligne")
    
    # Labels et champs de saisie pour ID, Nom, Prénom et Email
    labels = ["id_finger", "Nom:", "Prénom:"]
    nouvelles_valeurs = []

    for i, label in enumerate(labels):
        Label(fenetre_ajout, text=label).grid(row=i, column=0, padx=5, pady=5)
        entree = Entry(fenetre_ajout)
        entree.grid(row=i, column=1, padx=5, pady=5)
        nouvelles_valeurs.append(entree)

    # Fonction pour détecter l'empreinte et ajouter la nouvelle ligne
    def detecter_et_ajouter():
        valeurs = [entree.get() for entree in nouvelles_valeurs]
        
        # Vérifier si l'ID saisi existe déjà dans la base de données
        if id_existe(valeurs[0]):
            inserer_dans_base_de_donnees(valeurs)
            tableau.insert("", "end", values=tuple(valeurs))
            fenetre_ajout.destroy()
        else:
            # Détecter l'empreinte
            port = 'COM8'
            arduino_connection = None
            try:
                arduino_connection = serial.Serial(port, 9600, timeout=1)
            except Exception as e:
                print("Problème de connexion série avec l'Arduino :", e)

            print("Mettez votre doigt sur le capteur...")
            while True:
                data = arduino_connection.readline().strip().decode('utf-8')
                if data.isdigit():
                    cursor.execute(query_select, (data,))
                    result = cursor.fetchone()
                    if result == valeurs[0]:
                        inserer_dans_base_de_donnees(valeurs)
                        print("Bien enregistré.")
                        tableau.insert("", "end", values=tuple(valeurs))
                    else:
                        print("Erreur: ID non valide.")
                

    # Bouton pour ajouter la ligne
    bouton_ajout = Button(fenetre_ajout, text="Ajouter", command=detecter_et_ajouter)
    bouton_ajout.grid(row=len(labels), columnspan=2, padx=5, pady=10)
 

    # Bouton pour ajouter la ligne
    bouton_ajout = Button(fenetre_ajout, text="Ajouter", command=ajouter_ligne)
    bouton_ajout.grid(row=len(labels), columnspan=2, padx=5, pady=10)

def inserer_dans_base_de_donnees(valeurs):
    # Se connecter à la base de données MySQL
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="gestion"  # Assurez-vous de remplacer par le nom de votre base de données
    )

    # Créer un curseur pour exécuter des requêtes SQL
    cursor = conn.cursor()

    # Exécuter une requête pour insérer les valeurs dans la table Inscriptions
    cursor.execute("INSERT INTO Inscriptions (id_finger, Nom, Prenom) VALUES (%s, %s, %s)",
                   (valeurs[0], valeurs[1], valeurs[2]))

    # Valider la transaction et fermer le curseur et la connexion à la base de données
    conn.commit()
    cursor.close()
    conn.close()

def id_existe(id_finger):
    # Vérifier si l'ID existe déjà dans la base de données
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="gestion"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Inscriptions WHERE id_finger = %s", (id_finger,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result is not None




import mysql.connector

def supprimer_entree(item_id):
    # Récupérer les valeurs de l'entrée sélectionnée dans le tableau
    valeurs = tableau.item(item_id, 'values')

    # Supprimer l'entrée sélectionnée dans le tableau
    tableau.delete(item_id)

    # Connexion à la base de données MySQL
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="gestion"  # Assurez-vous de remplacer par le nom de votre base de données
    )
    
    # Créer un curseur pour exécuter des requêtes SQL
    cursor = conn.cursor()

    # Exécuter une requête pour supprimer l'entrée correspondante dans la base de données
    cursor.execute("DELETE FROM Inscriptions WHERE id_finger = %s", (valeurs[0],))
    
    # Valider la transaction et fermer le curseur et la connexion à la base de données
    conn.commit()
    cursor.close()
    conn.close()


def modifier_entree(item_id, event):
    # Récupérer les valeurs actuelles dans le tableau
    valeurs_actuelles = tableau.item(item_id, 'values')
    
    # Récupérer l'ID de l'étudiant
    id_etudiant = valeurs_actuelles[0]

    # Créer une fenêtre de dialogue pour saisir les nouvelles valeurs
    fenetre_modifier = Toplevel(root)
    fenetre_modifier.title("Modifier")
    
    # Labels et champs de saisie pour Nom, Prénom et Email
    labels = ["Nom:", "Prénom:", "Email:"]
    nouveaux_valeurs = []

    for i, label in enumerate(labels):
        Label(fenetre_modifier, text=label).grid(row=i, column=0, padx=5, pady=5)
        entree = Entry(fenetre_modifier)
        entree.insert(0, valeurs_actuelles[i + 1])  # Remplir le champ avec la valeur actuelle à partir de l'index 1
        entree.grid(row=i, column=1, padx=5, pady=5)
        nouveaux_valeurs.append(entree)

    # Fonction pour mettre à jour les valeurs dans le tableau et la base de données
    def mettre_a_jour():
        # Récupérer les nouvelles valeurs saisies par l'utilisateur
        nouvelles_valeurs = [entree.get() for entree in nouveaux_valeurs]

        # Mettre à jour les valeurs dans le tableau
        tableau.item(item_id, values=(id_etudiant,) + tuple(nouvelles_valeurs))

        # Mettre à jour les valeurs dans la base de données
        mettre_a_jour_base_de_donnees(id_etudiant, nouvelles_valeurs)

        fenetre_modifier.destroy()

    # Bouton pour mettre à jour les valeurs
    bouton_maj = Button(fenetre_modifier, text="Mettre à jour", command=mettre_a_jour)
    bouton_maj.grid(row=len(labels), columnspan=2, padx=5, pady=10)


def mettre_a_jour_base_de_donnees(id_etudiant, nouvelles_valeurs):
    # Se connecter à la base de données MySQL
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="gestion"  # Assurez-vous de remplacer par le nom de votre base de données
    )
    
    # Créer un curseur pour exécuter des requêtes SQL
    cursor = conn.cursor()

    # Exécuter une requête pour mettre à jour les valeurs dans la table Inscriptions
    cursor.execute("UPDATE Inscriptions SET Nom = %s, Prenom = %s, Email = %s WHERE id_finger = %s", 
                   (nouvelles_valeurs[0], nouvelles_valeurs[1], nouvelles_valeurs[2], id_etudiant))
    
    # Valider la transaction et fermer le curseur et la connexion à la base de données
    conn.commit()
    cursor.close()
    conn.close()
def modifier_presence_absence(item_id):
    # Récupérer les valeurs actuelles dans le tableau
    valeurs_actuelles = tableau.item(item_id, 'values')
    
    # Récupérer l'ID de l'étudiant
    id_etudiant = valeurs_actuelles[0]

    # Créer une fenêtre de dialogue pour saisir les nouvelles valeurs
    fenetre_modifier = Toplevel(root)
    fenetre_modifier.title("Modifier Présence et Absence")
    
    # Labels et champs de saisie pour Présence et Absence
    labels = ["Présence:", "Absence:"]
    nouveaux_valeurs = []

    for i, label in enumerate(labels):
        Label(fenetre_modifier, text=label).grid(row=i, column=0, padx=5, pady=5)
        entree = Entry(fenetre_modifier)
        entree.insert(0, valeurs_actuelles[i + 3])  # Les colonnes "Présent" et "Absent" commencent à l'index 3
        entree.grid(row=i, column=1, padx=5, pady=5)
        nouveaux_valeurs.append(entree)

    # Fonction pour mettre à jour les valeurs dans le tableau et la base de données
    def mettre_a_jour_presence_absence():
        # Récupérer les nouvelles valeurs saisies par l'utilisateur
        nouvelles_valeurs = [entree.get() for entree in nouveaux_valeurs]

        # Mettre à jour les valeurs dans le tableau
        tableau.item(item_id, values=(id_etudiant,) + valeurs_actuelles[1:3] + tuple(nouvelles_valeurs))

        # Mettre à jour les valeurs dans la base de données
        mettre_a_jour_base_de_donnees_presence_absence(id_etudiant, nouvelles_valeurs)

        fenetre_modifier.destroy()

    # Bouton pour mettre à jour les valeurs
    bouton_maj = Button(fenetre_modifier, text="Mettre à jour", command=mettre_a_jour_presence_absence)
    bouton_maj.grid(row=len(labels), columnspan=2, padx=5, pady=10)


def mettre_a_jour_base_de_donnees_presence_absence(id_etudiant, nouvelles_valeurs):
    # Se connecter à la base de données MySQL
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="gestion"
    )
    
    # Créer un curseur pour exécuter des requêtes SQL
    cursor = conn.cursor()

    # Exécuter une requête pour mettre à jour les valeurs dans la table Inscriptions
    cursor.execute("UPDATE Inscriptions SET Présent = %s, Absent = %s WHERE id_finger = %s", 
                   (nouvelles_valeurs[0], nouvelles_valeurs[1], id_etudiant))
    
    # Valider la transaction et fermer le curseur et la connexion à la base de données
    conn.commit()
    cursor.close()
    conn.close()

from tkinter import messagebox


def create_account_interface():
    global name_entry, email_entry, password_entry, confirm_password_entry, account_canvas
    
    # Hide the login interface
    logo.place_forget()
    
    # Create a new canvas for the account creation interface
    account_canvas = Canvas(root, width=450, height=350, bg="#008080")
    account_canvas.place(relx=0.5, rely=0.5, anchor=CENTER)
    
    # Labels
    Label(account_canvas, text="Nom et prénom:", font=('arial', 15), bg="#008080", fg="#ffffff").place(x=20, y=50)
    Label(account_canvas, text="Email:", font=('arial', 15), bg="#008080", fg="#ffffff").place(x=20, y=90)
    Label(account_canvas, text="Password:", font=('arial', 15), bg="#008080", fg="#ffffff").place(x=20, y=130)
    Label(account_canvas, text="Confirmer Password:", font=('arial', 15), bg="#008080", fg="#ffffff").place(x=20, y=170)
    
    # Entry widgets for name, email, password, and confirm password
    name_entry = Entry(account_canvas, width=20, relief=FLAT, font=('arial', 15))
    name_entry.place(x=220, y=50)
    
    email_entry = Entry(account_canvas, width=20, relief=FLAT, font=('arial', 15))
    email_entry.place(x=220, y=90)
    
    password_entry = Entry(account_canvas, width=20,  relief=FLAT, font=('arial', 15))
    password_entry.place(x=220, y=130)
    
    confirm_password_entry = Entry(account_canvas, width=20,  relief=FLAT, font=('arial', 15))
    confirm_password_entry.place(x=220, y=170)
    
    # Buttons for registering and returning to the login interface
    register_button = Button(account_canvas, text="Enregistrer", command=register_account, bg="#F5F5DC", font=('arial', 15))
    register_button.place(x=250, y=220)
    
    return_button = Button(account_canvas, text="Retour", command=lambda: return_to_login_interface(account_canvas), bg="#A52A2A", font=('arial', 15))
    return_button.place(x=180, y=220)

def return_to_login_interface(account_canvas):
    # Remove the account creation interface and show the login interface again
    account_canvas.destroy()
    logo.place(relx=0.5, rely=0.5, anchor=CENTER)

root = Tk()
root.title("Gestion d'appel")
root.geometry("950x550+180+50")

logo = Canvas(root, width=450, height=350, bg="#008080")
logo.place(relx=0.5, rely=0.5, anchor=CENTER)

Label(logo, text="Email:", font=('arial', 15), bg="#008080", fg="#ffffff").place(x=40, y=90)
Label(logo, text="Mot de passe:", font=('arial', 15), bg="#008080", fg="#ffffff").place(x=40, y=170)

identifiant_entry = Entry(logo, width=30, relief=FLAT, font=('arial', 15))
identifiant_entry.place(x=40, y=130)

mdp_entry = Entry(logo, width=30, relief=FLAT, font=('arial', 15), show="*")
mdp_entry.place(x=40, y=210)

identifiant_label = Label(logo, text="", fg="red", font=('arial', 15), bg="#008080")
identifiant_label.place(x=350, y=90)

mdp_label = Label(logo, text="", fg="red", font=('arial', 15), bg="#008080")
mdp_label.place(x=350, y=170)

identifiant_entry.bind("<Key>", lambda event: on_entry_change(event, identifiant_label))
mdp_entry.bind("<Key>", lambda event: on_entry_change(event, mdp_label))

toggle_button = Button(logo, text="⦾", command=toggle_password_visibility, bg="#fff", fg="black", font=('arial', 9))
toggle_button.place(x=350, y=210)

oublie_button = Button(logo, text="Mot de passe oublié", relief=FLAT, bg="#008080", fg="#fff", font=('arial', 12))
oublie_button.place(x=40, y=240)

login_button = Button(logo, text="Se connecter", command=login, bg="#F5F5DC", font=('arial', 12))
login_button.place(x=100, y=270)

creecompt_button = Button(logo, text="Créer un compte", relief=FLAT, bg="#F5F5DC", font=('arial', 12), command=create_account_interface)
creecompt_button.place(x=100, y=310)

logo_title = Label(logo, text="Gestion d'appel", font=('arial', 25, 'bold'), bg="#008080", fg="black")
logo_title.place(relx=0.5, rely=0.1, anchor=CENTER)

is_password_visible = False
tableau_presence = None
date_combobox = None
tableau_absence = None

root.mainloop()
