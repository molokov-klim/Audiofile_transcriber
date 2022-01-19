from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import (QMainWindow, QTextEdit,
                             QAction, QFileDialog, QApplication)

# importing libraries
import speech_recognition as sr
import os
import pydub
import glob
import ctypes
from pydub import AudioSegment
from pydub.silence import split_on_silence
import shutil
import datetime

filename = "no.wav"

# create a speech recognition object
r = sr.Recognizer()

Form, _ = uic.loadUiType("MainWindow.ui")


class Ui(QtWidgets.QMainWindow, Form):

    def __init__(self):
        super(Ui, self).__init__()
        self.setupUi(self)
        self.openFile.triggered.connect(self.openFile_triggered)
        self.saveFile.triggered.connect(self.saveFile_triggered)
        self.m4a_to_wav.triggered.connect(self.m4a_to_wav_triggered)

    def openFile_triggered(self):
        print("openFile_triggered")
        try:
            shutil.rmtree("audio-chunks")
        except OSError as e:
            print("Ошибка удаления, папки не существует")
        self.outputEdit.setText(get_large_audio_transcription())
        ctypes.windll.user32.MessageBoxW(0, "Транскрибация завершена", "Информация", 0)

    def saveFile_triggered(self):
        print("saveFile_triggered")
        text_filename = QFileDialog.getSaveFileName(self)[0]
        try:
            f = open(text_filename, 'w+')
            text = self.outputEdit.toPlainText()
            f.write(text)
            f.close()
        except FileNotFoundError:
            print("No such file")
        ctypes.windll.user32.MessageBoxW(0, "Файл успешно сохранен", "Информация", 0)

    def m4a_to_wav_triggered(self):
        # Convert all file extensions to m4a (if required)

        import os, sys

        folder = './'
        for filename in os.listdir(folder):
            infilename = os.path.join(folder, filename)
            if not os.path.isfile(infilename): continue
            oldbase = os.path.splitext(filename)
            newname = infilename.replace('.tmp', '.m4a')
            output = os.rename(infilename, newname)

        # Convert m4a extension files to wav extension files

        import os
        import argparse

        from pydub import AudioSegment

        formats_to_convert = ['.m4a']

        for (dirpath, dirnames, filenames) in os.walk("./"):
            for filename in filenames:
                if filename.endswith(tuple(formats_to_convert)):

                    filepath = dirpath + '/' + filename
                    (path, file_extension) = os.path.splitext(filepath)
                    file_extension_final = file_extension.replace('.', '')
                    try:
                        track = AudioSegment.from_file(filepath,
                                                       file_extension_final)
                        wav_filename = filename.replace(file_extension_final, 'wav')
                        wav_path = dirpath + '/' + wav_filename
                        print('CONVERTING: ' + str(filepath))
                        file_handle = track.export(wav_path, format='wav')
                        os.remove(filepath)
                    except:
                        print("ERROR CONVERTING " + str(filepath))

        ctypes.windll.user32.MessageBoxW(0, "Конвертация завершена", "Информация", 0)





def get_large_audio_transcription():
    """
    Splitting the large audio file into chunks
    and apply speech recognition on each of these chunks
    """
    # open the audio file using pydub
    path_to_file = QFileDialog.getOpenFileName(QtWidgets.QMainWindow(), 'Open file', '/')[0]
    print(path_to_file)
    sound = AudioSegment.from_wav(path_to_file)
    print("file duration: " + str(datetime.timedelta(seconds=int(sound.duration_seconds))))

    # split audio sound where silence is 700 miliseconds or more and get chunk
    chunks = split_on_silence(sound,
                              # experiment with this value for your target audio file
                              min_silence_len=1000,
                              # adjust this per requirement
                              silence_thresh=sound.dBFS - 14,
                              # keep the silence for 1 second, adjustable as well
                              keep_silence=1000,
                              )
    print("splitting done")
    folder_name = "audio-chunks"
    # create a directory to store the audio chunks
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)
    whole_text = ""
    whole_time = 0
    # process each chunk
    for i, audio_chunk in enumerate(chunks, start=1):
        # export audio chunk and save it in
        # the `folder_name` directory.
        chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
        audio_chunk.export(chunk_filename, format="wav")
        # recognize the chunk
        with sr.AudioFile(chunk_filename) as source:
            audio_listened = r.record(source)
            print(chunk_filename, ":", str(datetime.timedelta(seconds=int(source.DURATION))))
            whole_time += source.DURATION
            # print("whole_time: " + str(datetime.timedelta(seconds=int(whole_time))))
            # try converting it to text
            try:
                text = r.recognize_google(audio_listened, language="ru-RU")
            except sr.UnknownValueError as e:
                print("Error RU:", str(e))
            else:
                text = f"{text.capitalize()}. "
                print(str(datetime.timedelta(seconds=int(whole_time))), ":", text)
                whole_text += str(datetime.timedelta(seconds=int(whole_time)))
                whole_text += ": "
                whole_text += text
                whole_text += "\n"
    # return the text for all chunks detected
    return whole_text



if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    w = Ui()
    w.show()  # show window
    sys.exit(app.exec_())



## Button styles ctypes:
# 0 : OK
# 1 : OK | Cancel
# 2 : Abort | Retry | Ignore
# 3 : Yes | No | Cancel
# 4 : Yes | No
# 5 : Retry | No
# 6 : Cancel | Try Again | Continue

## To also change icon, add these values to previous number
# 16 Stop-sign icon
# 32 Question-mark icon
# 48 Exclamation-point icon
# 64 Information-sign icon consisting of an 'i' in a circle