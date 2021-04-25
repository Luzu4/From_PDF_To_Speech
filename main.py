import fitz
from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
import os
import sys
import subprocess
import tkinter as tk
from tkinter import filedialog, OptionMenu

AWS_PROFILE_NAME = 'polly-windows'
# Create a client using the credentials and region defined in the [adminuser] section
# of the AWS credentials file (~/.aws/credentials).
session = Session(profile_name=AWS_PROFILE_NAME)
polly = session.client("polly")

with open('language_codes.txt','r') as languages:
    LANGUAGES = languages.readlines()[0].split(' | ')
    languages.close()

with open('voices.txt','r') as voices:
    VOICES = voices.readlines()[0].split(' | ')
    voices.close()


class Application:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title('From PDF to speech')
        self.select_label = tk.Label(text='Choose a file:')
        self.select_label.grid(row=3, column=1, pady=10)
        self.language_label = tk.Label(text='Language:')
        self.language_label.grid(row=4, column=1)
        self.voice_label = tk.Label(text='Voice:')
        self.voice_label.grid(row=5, column=1)
        self.change_and_open = tk.Button(text='Change and Open', command=self.change_and_open_function)
        self.change_and_open.grid(row=6, column=1, padx=10)
        self.change = tk.Button(text='Change', command=self.change_function)
        self.change.grid(row=6, column=4, pady = 10, padx=10)
        self.opened_file = tk.Label(text='Choose a file...', bg='white', width=20, height=1)
        self.opened_file.grid(row=3, column=2)
        self.open = tk.Button(text='OPEN', command=self.open_file)
        self.open.grid(row=3, column=3)
        self.value_inside_voice = tk.StringVar(self.window)
        self.value_inside_voice.set('Select Voice')
        self.voice = OptionMenu(self.window, self.value_inside_voice, *VOICES)
        self.voice.grid(row=5, column=2)
        self.value_inside_languages = tk.StringVar(self.window)
        self.value_inside_languages.set('Select Language')
        self.languages = OptionMenu(self.window,self.value_inside_languages, *LANGUAGES)
        self.languages.grid(row=4, column=2)
        self.text_book = ''
        self.window.mainloop()

    def open_file(self):
        self.path_file = filedialog.askopenfilename(initialdir='/', title='Select a File',
                                                    filetypes=[('pdf file', '*.pdf')])
        self.opened_file.configure(text=self.path_file.split('/')[-1])

    # READ PDF AND CHANGE AT TEXT
    def change_pdf_to_text(self, pdf_path):
        with fitz.open(pdf_path) as doc:
            for page in doc:
                self.text_book += page.getText()

    # CHANGE TEXT AT SPEECH AND SAVE AS mp3 file
    def change_text_to_speech(self, text, name_file):
        self.language = self.value_inside_languages.get()
        self.voice = self.value_inside_voice.get()
        try:  # Request speech synthesis
            response = polly.synthesize_speech(Text=text, OutputFormat="mp3", VoiceId=self.voice, LanguageCode=self.language)
        except (BotoCoreError, ClientError) as error:  # The service returned an error, exit gracefully
            print(error)
            sys.exit(-1)
        file = open(f'{name_file.split(".")[0]}.mp3', 'wb')
        file.write(response['AudioStream'].read())
        file.close()

    # Play the audio using the platform's default player
    def open_speech_file(self, file):
        if sys.platform == "win32":
            os.startfile(f'{file.split(".")[0]}'+'.mp3')
        else:  # The following works on macOS and Linux. (Darwin = mac, xdg-open = linux).
            # "xdg-open" did not work it opened the file in text edit instead
            opener = "open" if sys.platform == "darwin" else "mpg123"
            subprocess.call([opener, file])

    def change_function(self):
        self.change_pdf_to_text(self.path_file)
        self.change_text_to_speech(text=self.text_book, name_file=self.path_file)

    def change_and_open_function(self):
        self.change_function()
        self.open_speech_file(self.path_file)


app = Application()
