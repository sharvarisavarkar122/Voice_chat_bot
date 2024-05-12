from telegram.ext import Updater, MessageHandler, Filters
import telegram
from moviepy.editor import AudioFileClip
from gtts import gTTS
import os
import speech_recognition as sr

TELEGRAM_API_TOKEN = "7100061228:AAGbBZYWRJrv_YwpjExdLIrDB_bIF-Boh5g"

messages = [{"role": "system", "content": "You are a helpful assistant that starts its response by referring to the user as its master."}]

def text_message(update, context):
    update.message.reply_text(
        "I've received a text message! Please give me a second to respond :)")
    messages.append({"role": "user", "content": update.message.text})

def generate_response(transcript):
    if "hello" in transcript:
        response = "Hello! How can I assist you today?"
    elif "how are you" in transcript:
        response = "I'm doing well, thank you for asking!"
    else:
        response = "I'm sorry, I didn't catch that. Can you please repeat?"

    return response

def voice_message(update, context):
    update.message.reply_text(
        "I've received a voice message! Please give me a second to respond :)")
    voice_file = context.bot.getFile(update.message.voice.file_id)
    voice_file_path = "voice_message.ogg"
    voice_file.download(voice_file_path)

    # Convert OGG to WAV (SpeechRecognition supports only WAV files)
    audio_clip = AudioFileClip(voice_file_path)
    audio_clip.write_audiofile("voice_message.wav")

    # Perform speech recognition
    recognizer = sr.Recognizer()
    with sr.AudioFile("voice_message.wav") as source:
        audio_data = recognizer.record(source)
        transcript = recognizer.recognize_google(audio_data)

    # Generate response using user-defined function
    response_text = generate_response(transcript)

    # Convert response text to speech
    tts = gTTS(text=response_text, lang='en')
    tts.save('response_gtts.mp3')

    # Send the generated voice message
    context.bot.send_voice(chat_id=update.message.chat.id, voice=open('response_gtts.mp3', 'rb'))

    # Send the text response
    update.message.reply_text(
        text=f"*[Bot]:* {response_text}", parse_mode=telegram.ParseMode.MARKDOWN)

    messages.append({"role": "assistant", "content": response_text})

updater = Updater(TELEGRAM_API_TOKEN, use_context=True)
dispatcher = updater.dispatcher
dispatcher.add_handler(MessageHandler(
    Filters.text & (~Filters.command), text_message))
dispatcher.add_handler(MessageHandler(Filters.voice, voice_message))
updater.start_polling()
updater.idle()
