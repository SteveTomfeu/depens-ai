from  openai import OpenAI
import os
import re
from dotenv import load_dotenv

load_dotenv()
deep_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key= deep_key ,base_url= "https://api.deepseek.com")

def structured_data(spending_text):
    syst = """
    Tu es un assistant intelligent de dépense. Je souhaite te donner une description de mes dépenses. Transforme la description en format JSON avec les champs suivants STRICTEMENT SANS AUCUN FORMATAGE MARKDOWN :
    
    {
        "designation": "description", 
        "moyen_paiement": ["Cash", "mobile money", "orange money", "Carte de crédit"],
        "categorie": ["transport", "shopping", "electricité", "eau", "loyer", "voiture", "télévision", "sport", "santé", "loisirs", "autres"],
        "montant": nombre
    }
    
    Règles strictes :
    - Pas de ```json ou ``` autour du JSON
    - Aucun texte avant/apès le JSON
    - Toujours utiliser les guillemets doubles
    - Maintenir la casse exacte des valeurs
    - Vérifier l'appartenance aux listes autorisées
    """
    
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages= [
            {"role": "system", "content": syst},
            {"role": "user", "content": spending_text},
        ],
        stream=False
    )
    answer = response.choices[0].message.content
    cleaned_json = re.sub(r'^```json|```$', '', answer, flags=re.MULTILINE).strip()
    return cleaned_json

def text_to_sql(question):
    syst = """
        J'ai une table SQL nommée "depenses" avec les colonnes suivantes :

            id INTEGER PRIMARY KEY,
            designation TEXT,
            moyen_paiement TEXT,
                categorie TEXT,
                montant REAL,
                date DATE,

            Transforme la question suivante en requête SQL qui répond à la question. Tu ne retournes que la requête SQL, aucun autre text introductif:
                

    """
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages= [
            {"role": "system", "content": syst},
            {"role": "user", "content": question},
        ],
        stream=False
    )

    answer = response.choices[0].message.content
    cleaned_json = re.sub(r'^```sql|```$', '', answer, flags=re.MULTILINE).strip()
    return cleaned_json
# print(deep_key)
# r = text_to_sql("Combien ai-je dépensé ce mois en transport ?")
# print(r)

def reformule_answer(user_question, sql_result):
    syst = """
    En te basant sur le table SQL dont le schema est le
    suivant, génère une réponse en langage naturel  : 
    id INTEGER PRIMARY KEY,
        designation TEXT,
        moyen_paiement TEXT,
            categorie TEXT,
            montant REAL,
            date DATE
    """
    quest = f'''Voici la question qu'a posé l'utilisateur : {user_question}
    La réponse SQL : {sql_result}
    Si la réponse est un montant, l'unité monetaire est fcfa
    '''

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages= [
            {"role": "system", "content": syst},
            {"role": "user", "content": quest},
        ],
        stream=False
    )
    answer = response.choices[0].message.content
    
    return answer
