import pyaudio
import deepgram
import os
import dotenv
from dotenv import load_dotenv
import google.generativeai as genai
from deepgram import DeepgramClient,PrerecordedOptions,FileSource,SpeakOptions
import time
load_dotenv
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model=genai.GenerativeModel("gemini-pro")
stt =DeepgramClient(os.getenv('DG_API_KEY'))
def get_gemini_response(question):
    response=model.generate_content(question)
    return str(response.text)
def get_audio(text):
    print(text)
    response=get_gemini_response(text)
    print(response)
    SPEAK_OPTIONS = {"text": response}
    filename ='output.wav'
    try:
        options = SpeakOptions(
        model="aura-asteria-en",
        encoding="linear16",
        container="wav"
        )
        res=stt.speak.v('1').save(filename, SPEAK_OPTIONS, options)
    except Exception as e:
        response = None
    return str(response)