#! /usr/bin/python3


import speech_recognition as sr
import sqlite3
import os
import sys
from subprocess import call as run
from viki_utils import *
from multiprocessing import Process, Lock, Queue, Manager
from multiprocessing.connection import wait


def lual():
    s_mem = {}  # short term memory; make it easier to pass stuff around

    if not os.path.exists('memory'):
        # ensure the memory folder exists
        os.makedirs('memory')
    s_mem['conn'] = sqlite3.connect("memory/mem.db")
    s_mem['tokens'] = get_tokens()
    s_mem['mode'] = "cmd"  # lrn, dct, prg
    #wav_pos = ""
    s_mem['llock'] = Manager().Lock()  # listen lock
    s_mem['mlock'] = Manager().Lock()  # memory lock
    s_mem['mainq'] = Manager().Queue()  # main queue
    s_mem['listening'] = False
    #s_mem['listener'] = None
    s_mem['action'] = None

    while True:

        if not s_mem['listening']:
            # ensure a listener is running
            s_mem['listener'] = Process(target=listen, args=((s_mem, ))).start()
        msg = None
        s_mem['llock'].acquire()

        if s_mem['mainq'].empty():
            # TODO: convert to sentinel method
            s_mem['llock'].release()
            sleep(100)
            continue

        while not s_mem['mainq'].empty():
            # rebuild s_mem
            itm = s_mem['mainq'].get()
            msg[itm[0]] = itm[1]
        s_mem['llock'].release()
        s_mem = msg


def next_train_wav(cnt=0):
    base = "training/arctic_"
    pad = ""

    if cnt < 999:
        pad += "0"

        if cnt < 99:
            pad += "0"

            if cnt < 9:
                pad += "0"

    while True:
        cnt += 1

        if os.path.isfile(base + pad + str(cnt) + ".wav"):
            continue

        else:
            return pad + str(cnt)

def make_adapt(trans, live=False):
    num = trans["wavs"]
    os.link("memory/rec_" + trans["time"] + ".wav", "training/arctic_" + num + ".wav")

    if trans["text"] != "":
        sentence = trans["text"]

    else:
        sentence = trans["g"]
    print("arctic_" + num, "training/arctic20.fileids")
    print("<s> " + sentence + " </s> (arctic_" + num + ")", "training/arctic20.transcription")
    return num

def understand(s_mem, action='default'):
    trans = s_mem['trans']
    recog = s_mem['recog']
    audio = s_mem['audio']

    if action == 'default':
        sentinels = []
        engines = ['use_ps', 'use_wit']
        s_mem['subq'] = Queue()

        for engine in engines:
            # parallel recognition
            proc = Process(target=understand, args=((s_mem, engine)))
            proc.start()
            sentinels.append(proc.sentinel)

        while sentinels:

            for sentinel in wait(sentinels):
                # remove ready (terminated) processes and check results queue
                sentinels.remove(sentinel)
                msg = s_mem['subq'].get()
                s_mem['trans'][msg[0]] = msg[1]

        if len(s_mem['trans']['wit']) < 4:
            trans['text'] = 'ignore'
        answer(s_mem)
        return

    if action == 'use_ps':
        # recognize speech using PocketSphinx

        try:
            text = recog.recognize_sphinx(audio)
            s_mem['subq'].put(['ps', text])
            return

        except sr.UnknownValueError:
            print("Sphinx didn't understand anything you said...")

        except sr.RequestError as e:
            print("Sphinx error; {0}".format(e))

    if action == 'use_wit':
        # recognize speech using Wit.ai
        WIT_AI_KEY = s_mem['tokens']['wit.ai']

        try:
            text = recog.recognize_wit(audio, key=WIT_AI_KEY)
            s_mem['subq'].put(['wit', text])
            return

        except sr.UnknownValueError:
            print("Wit.ai didn't understand anything you said...")

        except sr.RequestError as e:
            print("Could not request results from Wit.ai service; {0}".format(e))

    if action == 'use_ggl':
    #if trans["ps"] == trans["wit"] or len(trans["wit"].split()) < 4:
        # recognize speech using Google Speech Recognition
        # need to use sparingly since API use is limited

        try:
            # for testing purposes, we're just using the default API key
            # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
            # instead of `r.recognize_google(audio)`
            text = recog.recognize_google(audio)
            s_mem['subq'].put(['ggl', text])
            return

        except sr.UnknownValueError:
            print("Google didn't understand anything you said...")

        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
    print('Error: Invalid action passed')

def answer(s_mem):
    #s_mem['mlock'].acquire()
    conn = s_mem['conn']
    trans = s_mem['trans']

    if trans["ps"] == "reload" or trans["ggl"] == "reload" or trans["wit"] == "reload":
        s_mem['action'] = 'reload'
        s_mem['mainq'].put(s_mem)
        return

    if trans["text"] == "ignore":
        # ignore triffles
        print('Not committing to long term memory:')
        print(trans)
        return
    match = check_match(trans)

    with open("memory/rec_" + trans["time"] + ".wav", "wb") as f:
        f.write(s_mem['audio'].get_wav_data())

    c = conn.cursor()

    try:
        # Ensure the target table exists
        c.execute("SELECT * FROM Ears ORDER BY time")

    except sqlite3.Error as e:

        if e.args[0] == "no such table: Ears":
            c.execute("CREATE TABLE Ears (time, ps_trans, g_trans, wit_trans, ibm_trans, att_trans, text, match)")

        else:
            print("Error:", e.args[0])
    entry = (trans["time"], trans["ps"], trans["ggl"], "", "", "", trans["text"], match)
    c.execute("INSERT INTO Ears VALUES (?, ?, ?, ?, ?, ?, ?, ?)", entry)
    conn.commit()
    c.close()

    if s_mem['mode'] == "lrn" and trans["ps"] != "training mode":
        pass
    #conn.close()
    #s_mem['mlock'].release()
    sys.exit(0)

def speak_out(text, voice='slt', echo=True):
    # TTS via mimic
    run('mimic -voice ' + voice + ' "' + text + '" speech.wav')
    run('amarok speech.wav')
    run('rm speech.wav')

    if echo:
        print(text)

def listen(s_mem):
    s_mem['recog'] = sr.Recognizer()
    s_mem['audio'] = None
    tstamp = '00'
    s_mem['trans'] = {"time" : "00", "ps" : "", "ggl" : "", "wit" : "", "ibm" : "", "att" : "", "text" : "", "wavs" : ''}

    with sr.Microphone() as source:
        s_mem['listening'] = True
        print('Now listening...')
        s_mem['audio'] = s_mem['recog'].listen(source)
        print('Sending audio for processing!')
        s_mem['trans']['time'] = timestamp()
    s_mem['listening'] = False
    s_mem['llock'].acquire()

    for itm in s_mem:
        # break down s_mem to avoid 'Unserializable message' error
        s_mem['mainq'].put([itm, s_mem[itm]])
    s_mem['llock'].release()
    understand(s_mem)
    #Process(target=understand, args=(s_mem)).start()


''' Setup these later as fallbacks/alternates/trainers
# recognize speech using IBM Speech to Text
IBM_USERNAME = "INSERT IBM SPEECH TO TEXT USERNAME HERE" # IBM Speech to Text usernames are strings of the form XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
IBM_PASSWORD = "INSERT IBM SPEECH TO TEXT PASSWORD HERE" # IBM Speech to Text passwords are mixed-case alphanumeric strings
try:
    print("IBM Speech to Text thinks you said " + r.recognize_ibm(audio, username=IBM_USERNAME, password=IBM_PASSWORD))
except sr.UnknownValueError:
    print("IBM Speech to Text could not understand audio")
except sr.RequestError as e:
    print("Could not request results from IBM Speech to Text service; {0}".format(e))

# recognize speech using AT&T Speech to Text
ATT_APP_KEY = "INSERT AT&T SPEECH TO TEXT APP KEY HERE" # AT&T Speech to Text app keys are 32-character lowercase alphanumeric strings
ATT_APP_SECRET = "INSERT AT&T SPEECH TO TEXT APP SECRET HERE" # AT&T Speech to Text app secrets are 32-character lowercase alphanumeric strings
try:
    print("AT&T Speech to Text thinks you said " + r.recognize_att(audio, app_key=ATT_APP_KEY, app_secret=ATT_APP_SECRET))
except sr.UnknownValueError:
    print("AT&T Speech to Text could not understand audio")
except sr.RequestError as e:
    print("Could not request results from AT&T Speech to Text service; {0}".format(e))
'''
