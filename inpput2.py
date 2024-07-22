
# This code is used to convert the audio input to text and then convert the text to audio output using the Deepgram and Google Generative AI services.

import pyaudio
import deepgram
import os
from dotenv import load_dotenv
import google.generativeai as genai
from deepgram import DeepgramClient,PrerecordedOptions,FileSource,SpeakOptions
import numpy as np
import soundfile as sf
import sys
import wave
import time
def play_audio(filename):
    # Open the file
    wf = wave.open(filename, 'rb')

    # Create a PyAudio instance
    p = pyaudio.PyAudio()

    # Open a stream
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    # Read data from the file
    data = wf.readframes(1024)

    # Play the audio by writing the data to the stream
    while data:
        stream.write(data)
        data = wf.readframes(1024)

    # Close and terminate everything properly
    stream.stop_stream()
    stream.close()
    p.terminate()

# Redirect STDERR to null
sys.stderr = open(os.devnull, 'w')


load_dotenv()
API_KEY=os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model=genai.GenerativeModel("gemini-pro")
def get_gemini_response(question):
    response=model.generate_content(question)
    return response.text
silence_threshold = 0.7
import wave
# Initialize your services
audio = pyaudio.PyAudio()
stt =DeepgramClient(os.getenv('DG_API_KEY'))
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

try:
    # Open the audio input stream
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    cnt=0
    frames=[]
    while True:
        data = stream.read(CHUNK)
        frames.append(data)
        amplitude = np.sqrt(np.mean(np.square(np.frombuffer(data, dtype=np.int16).astype(np.float32))))
        print(amplitude)
        if amplitude < silence_threshold:
            cnt+=1
            if(cnt>50):
                end_speaking_time = time.time()
                break
        # Read from the audio input stream
    stream.stop_stream()
    stream.close()
    audio.terminate()
    wf = wave.open("outpur.wav", 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    with open("outpur.wav", "rb") as f:
        buffer_data=f.read()
    payload:FileSource={
        'buffer':buffer_data,
    }
    option=PrerecordedOptions(
    model="nova-2",
    smart_format=True,
    )
    transcription = stt.listen.rest.v("1").transcribe_file(payload,option)
    stt_response_time = time.time()
    print(transcription.to_json(indent=4))  # Print the transcription
    text=transcription['results']['channels'][0]['alternatives'][0]["transcript"]
    if text=="\n":
        print("No audio detected")
    else:
        print(text)
        response=get_gemini_response(text)
        llm_response_time = time.time()
        print(response)
        SPEAK_OPTIONS = {"text": response}
        filename = "output.wav"
        try:
            options = SpeakOptions(
            model="aura-asteria-en",
            encoding="linear16",
            container="wav"
            )
            res=stt.speak.v('1').save(filename, SPEAK_OPTIONS, options)
            tts_start_time = time.time()
            print(res.to_json(indent=4))
            play_audio("output.wav")
            stt_total_time = stt_response_time - end_speaking_time
            print(f"Total Time for STT post user stopped speaking: {stt_total_time} seconds")
            llm_total_time = llm_response_time - stt_response_time
            print(f"Time for Complete Response From LLM: {llm_total_time} seconds")
            tts_total_time = tts_start_time - end_speaking_time
            print(f"Total time from when user stopped speaking and TTS generated first speech: {tts_total_time} seconds")
        except Exception as e:
            print(f"Exception: {e}")
except Exception as e:
    print(f"Exception: {e}")