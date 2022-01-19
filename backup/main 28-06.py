from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import (QMainWindow, QTextEdit,
    QAction, QFileDialog, QApplication)

# importing libraries
import speech_recognition as sr
import os
from pydub import AudioSegment
from pydub.silence import split_on_silence

filename = "no.wav"

# create a speech recognition object
r = sr.Recognizer()

Form, _ = uic.loadUiType("MainWindow.ui")

class Ui(QtWidgets.QMainWindow, Form):
    def __init__(self):
        super(Ui, self).__init__()
        self.setupUi(self)
        self.openFile.triggered.connect(self.openFile_triggered)

    def openFile_triggered(self):
        print("pressed")
        get_simple_audio_trascription()
        #print("\nFull text:", get_simple_audio_trascription(path))
        #Ui.outputEdit.textCursor().insertHtml(get_simple_audio_trascription(path))

def get_large_audio_transcription(path):
    """
    Splitting the large audio file into chunks
    and apply speech recognition on each of these chunks
    """
    # open the audio file using pydub
    sound = AudioSegment.from_wav(path)
    # split audio sound where silence is 700 miliseconds or more and get chunks
    chunks = split_on_silence(sound,
        # experiment with this value for your target audio file
        min_silence_len = 500,
        # adjust this per requirement
        silence_thresh = sound.dBFS-14,
        # keep the silence for 1 second, adjustable as well
        keep_silence=500,
    )
    folder_name = "audio-chunks"
    # create a directory to store the audio chunks
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)
    whole_text = ""
    # process each chunk
    for i, audio_chunk in enumerate(chunks, start=1):
        # export audio chunk and save it in
        # the `folder_name` directory.
        chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
        audio_chunk.export(chunk_filename, format="wav")
        # recognize the chunk
        with sr.AudioFile(chunk_filename) as source:
            audio_listened = r.record(source)
            # try converting it to text
            try:
                text = r.recognize_google(audio_listened, language="ru-RU")
            except sr.UnknownValueError as e:
                print("Error:", str(e))
            else:
                text = f"{text.capitalize()}. "
                print(chunk_filename, ":", text)
                whole_text += text
    # return the text for all chunks detected
    return whole_text

def get_simple_audio_trascription():
    # obtain path to "english.wav" in the same folder as this script
    from os import path
    filename = QFileDialog.getOpenFileName(QtWidgets.QMainWindow(), 'Open file', '/')[0]
    print(filename)
    AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), filename)
    # use the audio file as the audio source
    with sr.AudioFile(AUDIO_FILE) as source:
        audio = r.record(source)  # read the entire audio file
    # recognize speech using Google Speech Recognition
    try:
        # for testing purposes, we're just using the default API key
        # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
        # instead of `r.recognize_google(audio)`
        print("Google Speech Recognition thinks you said " + r.recognize_google(audio, language="ru-RU"))

    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    w = Ui()
    w.show()  # show window
    sys.exit(app.exec_())






















