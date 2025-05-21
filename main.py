import json
import os
import re
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from google.cloud import speech
from dotenv import load_dotenv
from deepseek import structured_data, text_to_sql, reformule_answer
from sql_utils import save_to_sql, execute_query

load_dotenv()
speech_key = os.getenv("SPEECH_KEY")
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = speech_key
# Configuration
TOKEN = os.getenv("TELE_KEY")
SAVE_FOLDER = "voice_messages"

# Créer le dossier s'il n'existe pas
os.makedirs(SAVE_FOLDER, exist_ok=True)

def start(update: Update, context: CallbackContext):
    update.message.reply_text('Envoyez-moi un message vocal !')

def handle_voice(update: Update, context: CallbackContext):
    voice = update.message.voice or update.message.audio
    file = context.bot.get_file(voice.file_id)
    
    # Générer un nom de fichier unique
    file_name = f"voice_{update.message.message_id}"
    
    # Déterminer l'extension selon le type MIME
    if voice.mime_type == "audio/ogg":
        file_extension = ".ogg"
    else:
        file_extension = ".mp3"
    
    # Chemin complet du fichier
    file_path = os.path.join(SAVE_FOLDER, file_name + file_extension)
    
    # Télécharger et sauvegarder
    file.download(file_path)
    update.message.reply_text(f"Message vocal sauvegardé : {file_path}")
    #transcription
    transcript = transcribe_audio_gcp(file_path)
    update.message.reply_text(f"Vous avez dit : {transcript}")

    deep_answer = structured_data(transcript)
    update.message.reply_text(deep_answer)
    save_to_sql(deep_answer)
    update.message.reply_text("Entrée Sauvegardée")    
    
def transcribe_audio_gcp(file_path: str) -> str:
    """
    Transcrit un fichier audio en texte avec Google Cloud Speech-to-Text
    Retourne la transcription ou None en cas d'erreur
    """
    # Configuration Google Cloud
    client = speech.SpeechClient()

    try:
        with open(file_path, "rb") as audio_file:
            content = audio_file.read()

        audio = speech.RecognitionAudio(content=content)
        
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.OGG_OPUS,  # Adaptez selon le format
            sample_rate_hertz=48000,  # Fréquence d'échantillonnage typique pour les messages vocaux
            language_code="fr-FR",
            audio_channel_count = 1,    # Langue française
            enable_automatic_punctuation=True,
            model = 'phone_call'
        )

        response = client.recognize(config=config, audio=audio)
        
        if not response.results:
            return None
            
        return response.results[0].alternatives[0].transcript

    except Exception as e:
        print(f"Erreur de transcription: {str(e)}")
        return None
    
def get_spending_analytics(update, context):
    user_id = update.message.from_user.id
    text = update.message.text

    sql_query = text_to_sql(text)
    sql_answer = execute_query(sql_query)
    answer = reformule_answer(text, sql_answer)
    update.message.reply_text(answer)

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    # Gestion des commandes
    dp.add_handler(CommandHandler("start", start))
    
    # Gestion des messages vocaux
    dp.add_handler(MessageHandler(Filters.voice | Filters.audio, handle_voice))
    dp.add_handler(MessageHandler(Filters.text, get_spending_analytics))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()