import sqlite3
from datetime import datetime

# Créer une connexion à la base de données
conn = sqlite3.connect('depenses.db')
cursor = conn.cursor()

# Créer la table
cursor.execute('''
CREATE TABLE IF NOT EXISTS depenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    designation TEXT NOT NULL,
    categorie TEXT NOT NULL,
    moyen_paiement TEXT NOT NULL,
    montant REAL NOT NULL,
    date DATE NOT NULL
)
''')

# # Exemple d'insertion
# def ajouter_depense(designation, categorie, moyen_paiement, montant):
#     try:
#         cursor.execute('''
#         INSERT INTO depenses (designation, categorie, moyen_paiement, montant, date)
#         VALUES (?, ?, ?, ?, ?)
#         ''', (designation, categorie, moyen_paiement, montant, datetime.now().isoformat()))
        
#         conn.commit()
#         print("Dépense ajoutée avec succès!")
    
#     except sqlite3.Error as e:
#         print(f"Erreur SQLite : {str(e)}")
#         conn.rollback()

#Enregistrment des modifications
conn.commit()
# Fermer la connexion
conn.close()