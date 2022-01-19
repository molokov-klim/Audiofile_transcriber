import os
import pydub
import glob
import ctypes
import shutil
import datetime
import telebot
from PyQt5 import uic, QtWidgets, QtGui #, QtCore
from PyQt5.QtCore import Qt #QMimeData, QPoint
from PyQt5.QtWidgets import QInputDialog, QFileDialog #, QMainWindow, QTextEdit, QAction, QApplication
from PyQt5.QtGui import QTextCursor, QTextCharFormat, QBrush, QColor #, QImage, QTextDocument
import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence
#import argparse
#import sys
#import resources

filename = "no.wav"

# create telebot
TOKEN = '1864524481:AAEJLH0mOONadDUk1FM3-jna4a7S61u2ddo'
tb = telebot.TeleBot(TOKEN)

# create a speech recognition object
r = sr.Recognizer()

Form, _ = uic.loadUiType("MainWindow.ui")


class Ui(QtWidgets.QMainWindow, Form):
    # tb_id = 1353223764
    tb_id = 0

    def __init__(self):
        super(Ui, self).__init__()
        self.setupUi(self)
        self.openFile.triggered.connect(self.openFile_triggered)
        self.saveFile.triggered.connect(self.saveFile_triggered)
        self.m4a_to_wav.triggered.connect(self.m4a_to_wav_triggered)
        self.mp3_to_wav.triggered.connect(self.mp3_to_wav_triggered)
        self.flv_to_wav.triggered.connect(self.flv_to_wav_triggered)
        self.ogg_to_wav.triggered.connect(self.ogg_to_wav_triggered)
        self.searchButton.clicked.connect(self.searchButton_triggered)
        self.add_bot.triggered.connect(self.add_bot_triggered)
        self.show_ID.triggered.connect(self.show_ID_triggered)
        self.send.triggered.connect(self.send_triggered)
        self.about.triggered.connect(self.about_triggered)
        self.helpMe.triggered.connect(self.helpMe_triggered)
        self.test()

    def openFile_triggered(self):
        print("openFile_triggered")
        try:
            shutil.rmtree("audio-chunks")
        except OSError as e:
            print("Ошибка удаления, папки не существует")
        """
            Splitting the large audio file into chunks
            and apply speech recognition on each of these chunks
            """
        # open the audio file using pydub
        path_to_file = QFileDialog.getOpenFileName(QtWidgets.QMainWindow(), 'Open file', '/')[0]
        if path_to_file:
            print(path_to_file)
            sound = AudioSegment.from_wav(path_to_file)
            self.outputEdit.setText(
                "Продолжительность аудиофайла: " + str(datetime.timedelta(seconds=int(sound.duration_seconds))))

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
                    if self.eng.isChecked() == 1:
                        try:
                            text = r.recognize_google(audio_listened)
                        except sr.UnknownValueError as e:
                            print("Error RU:", str(e))
                        else:
                            text = f"{text.capitalize()}. "
                            print(str(datetime.timedelta(seconds=int(whole_time))), ":", text)
                            whole_text += str(datetime.timedelta(seconds=int(whole_time)))
                            whole_text += ": "
                            whole_text += text
                            whole_text += "\n"
                            try:
                                message = str(datetime.timedelta(seconds=int(whole_time))) + ": " + text
                                tb.send_message(self.tb_id, message)
                            except:
                                print("something wrong with tb.send_message(self.tb_id, text)")
                    if self.rus.isChecked() == 1:
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
                            try:
                                message = str(datetime.timedelta(seconds=int(whole_time))) + ": " + text
                                tb.send_message(self.tb_id, message)
                            except:
                                print("something wrong with tb.send_message(self.tb_id, text)")
            self.outputEdit.append(whole_text)
            ctypes.windll.user32.MessageBoxW(0, "Транскрибация завершена", "Информация", 0)

    def saveFile_triggered(self):
        print("saveFile_triggered")
        text_filename = QFileDialog.getSaveFileName(self)[0]
        try:
            f = open(text_filename, 'w+')
            text = self.outputEdit.toPlainText()
            f.write(text)
            f.close()
            ctypes.windll.user32.MessageBoxW(0, "Файл успешно сохранен", "Информация", 0)
        except FileNotFoundError:
            print("No such file")

    def m4a_to_wav_triggered(self):
        print("m4a_to_wav_triggered")
        # folder = 'C:/Users/Klim/Desktop/PYTHON'
        folder = QFileDialog.getExistingDirectory(
            caption='Выберите папку',
            options=QFileDialog.ShowDirsOnly,
            directory=''
        )
        # folder += "/"
        '''
        # Convert all file extensions to m4a (if required)
        for filename in os.listdir(folder):
            infilename = os.path.join(folder, filename)
            if not os.path.isfile(infilename): continue
            oldbase = os.path.splitext(filename)
            newname = infilename.replace('.tmp', '.m4a')
            output = os.rename(infilename, newname)
            '''
        # Convert m4a extension files to wav extension files
        formats_to_convert = ['.m4a']
        for (dirpath, dirnames, filenames) in os.walk(folder):
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

    def searchButton_triggered(self):
        print("searchButton_triggered")
        self.outputEdit.setFocus()

        text_to_find = self.searchEdit.displayText()
        index = self.outputEdit.toPlainText().find(text_to_find)
        cursor = QTextCursor(self.outputEdit.textCursor())
        format_of = QTextCharFormat()

        cursor.select(QTextCursor.Document)
        format_of.setBackground(QBrush(QColor(Qt.white)))
        cursor.setCharFormat(format_of)
        cursor.clearSelection()
        cursor.setCharFormat(format_of)

        cursor.setPosition(index, QTextCursor.MoveAnchor)
        self.outputEdit.setTextCursor(cursor)
        cursor.select(QTextCursor.WordUnderCursor)
        print(cursor.selectedText())
        print("index: ", index)
        print("self.outputEdit.textCursor().position(): ", self.outputEdit.textCursor().position())

        format_of.setBackground(QBrush(QColor(Qt.yellow)))
        cursor.setCharFormat(format_of)

        if text_to_find == "":
            cursor.select(QTextCursor.Document)
            format_of.setBackground(QBrush(QColor(Qt.white)))
            cursor.setCharFormat(format_of)

    def mp3_to_wav_triggered(self):
        print("mp3_to_wav_triggered")
        folder = QFileDialog.getExistingDirectory(
            caption='Выберите папку',
            options=QFileDialog.ShowDirsOnly,
            directory=''
        )
        mp3_files = glob.glob(folder + '/' + '*.mp3')
        for mp3_file in mp3_files:
            wav_file = os.path.splitext(mp3_file)[0] + '.wav'
            sound = pydub.AudioSegment.from_mp3(mp3_file)
            sound.export(wav_file, format='wav')
            os.remove(mp3_file)
        ctypes.windll.user32.MessageBoxW(0, "Конвертация завершена", "Информация", 0)

    def flv_to_wav_triggered(self):
        print("flv_to_wav_triggered")
        folder = QFileDialog.getExistingDirectory(
            caption='Выберите папку',
            options=QFileDialog.ShowDirsOnly,
            directory=''
        )
        flv_files = glob.glob(folder + '/' + '*.flv')
        for flv_file in flv_files:
            wav_file = os.path.splitext(flv_file)[0] + '.wav'
            sound = pydub.AudioSegment.from_flv(flv_file)
            sound.export(wav_file, format='wav')
            os.remove(flv_file)
        ctypes.windll.user32.MessageBoxW(0, "Конвертация завершена", "Информация", 0)

    def ogg_to_wav_triggered(self):
        print("ogg_to_wav_triggered")
        folder = QFileDialog.getExistingDirectory(
            caption='Выберите папку',
            options=QFileDialog.ShowDirsOnly,
            directory=''
        )
        ogg_files = glob.glob(folder + '/' + '*.ogg')
        for ogg_file in ogg_files:
            wav_file = os.path.splitext(ogg_file)[0] + '.wav'
            sound = pydub.AudioSegment.from_ogg(ogg_file)
            sound.export(wav_file, format='wav')
            os.remove(ogg_file)
        ctypes.windll.user32.MessageBoxW(0, "Конвертация завершена", "Информация", 0)

    def add_bot_triggered(self):
        text, ok = QInputDialog.getText(self, 'Ввод данных',
                                        'Введите Ваш Telegram ID:')
        if ok:
            self.tb_id = text
            self.show_ID_triggered()

    def show_ID_triggered(self):
        ctypes.windll.user32.MessageBoxW(0, self.tb_id, "Telegram ID", 0)

    def send_triggered(self):
        try:
            text = self.outputEdit.toPlainText()
            tb.send_message(self.tb_id, text)
        except:
            print("something wrong with tb.send_message(self.tb_id, text), about 110 line")

    def about_triggered(self):
        print("about_triggered")
        aboutForm.show()

    def helpMe_triggered(self):
        print("helpMe_triggered")
        helpForm.show()

    def test(self):
        print("start")


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('bird2.ico'))
    w = Ui()
    w.show()  # show window
    w.setWindowIcon(QtGui.QIcon('bird2.ico'))
    aboutForm = uic.loadUi("about.ui")
    helpForm = uic.loadUi("help.ui")
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

# Token Telegram Bot
# 1864524481:AAEJLH0mOONadDUk1FM3-jna4a7S61u2ddo
