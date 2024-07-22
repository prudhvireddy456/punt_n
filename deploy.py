from flask import Flask, request, redirect, url_for, flash, jsonify,render_template
from index import get_audio
import time
import wave
app=Flask(__name__)

@app.route('/',methods=['GET','POST'])
def hello():
    text=''
    if request.method=='POST':
        text=str(request.form['transcript'])
        print(text)
        res=get_audio(text)
        print(res)
        exp={
            'a':res
        }

        with wave.open('output.wav', 'rb') as wav_file:
            frames = wav_file.readframes(-1)
            params = wav_file.getparams()
        with wave.open('static/output.wav', 'wb') as wav_file:
            wav_file.setparams(params)
            wav_file.writeframes(frames)
    current_time = int(time.time())
    return render_template('index.html',result=exp,time=current_time)










if __name__ == "__main__":
    app.run(debug=True)