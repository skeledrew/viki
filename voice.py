#! /usr/bin/python3


import speech_recognition as sr
import time
import sqlite3
import os
import sys
from subprocess import call as run


def lual():
    recog = sr.Recognizer()
    audio = None
    tstamp = "00"
    conn = sqlite3.connect("memory/mem.db")
    mode = "cmd"  # lrn, dct, prg
    wav_pos = ""
    WIT_AI_KEY = "EOQY37HEGQHNKJ7M7IZMLVPETSDPF7QC" # Wit.ai keys are 32-character uppercase alphanumeric strings

    while True:
        match = 0
        trans = {"time" : "00", "ps" : "", "g" : "", "wit" : "", "ibm" : "", "att" : "", "text" : "", "wavs" : wav_pos}

        with sr.Microphone() as source:
            print("Whatchasay!")
            audio = recog.listen(source)
            print("I heard ya! Lemme process that...")
            trans["time"] = timestamp()
        #pid = os.fork()
        #
        #if not pid:
        #    # forking child
        #    sys.exit(0)  # disable fork until other things get sorted out
        #    understand(trans, recog, audio)

        #'''
        # recognize speech using PocketSphinx
        try:
            trans["ps"] = recog.recognize_sphinx(audio)
            print("Sphinx heard " + trans["ps"])

        except sr.UnknownValueError:
            print("Sphinx didn't understand anything you said...")

        except sr.RequestError as e:
            print("Sphinx error; {0}".format(e))

        # recognize speech using Wit.ai
        try:
            trans["wit"] = recog.recognize_wit(audio, key=WIT_AI_KEY)
            print("Wit.ai heard " + trans["wit"])

        except sr.UnknownValueError:
            print("Wit.ai didn't understand anything you said...")

        except sr.RequestError as e:
            print("Could not request results from Wit.ai service; {0}".format(e))

        if trans["ps"] == trans["wit"] or len(trans["wit"].split()) < 4:
            # don't use gsr
            print("Not using Google and totally ignoring this one.")
            trans["text"] = "ignore"

        else:
            # recognize speech using Google Speech Recognition
            try:
                # for testing purposes, we're just using the default API key
                # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
                # instead of `r.recognize_google(audio)`
                trans["g"] = recog.recognize_google(audio)
                print("Google heard " + trans["g"])

            except sr.UnknownValueError:
                print("Google didn't understand anything you said...")

            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))

        if trans["ps"] == "reload" or trans["g"] == "reload" or trans["wit"] == "reload":
            break

        if trans["text"] == "ignore":
            # ignore triffles
            continue
        match = check_match(trans)

        with open("memory/rec_" + trans["time"] + ".wav", "wb") as f:
            f.write(audio.get_wav_data())

        c = conn.cursor()

        try:
            # Ensure the target table exists
            c.execute("SELECT * FROM Ears ORDER BY time")

        except sqlite3.Error as e:

            if e.args[0] == "no such table: Ears":
                c.execute("CREATE TABLE Ears (time, ps_trans, g_trans, wit_trans, ibm_trans, att_trans, text, match)")

            else:
                print("Error:", e.args[0])
        entry = (trans["time"], trans["ps"], trans["g"], "", "", "", trans["text"], match)
        c.execute("INSERT INTO Ears VALUES (?, ?, ?, ?, ?, ?, ?, ?)", entry)
        conn.commit()
        c.close()

        if mode == "lrn" and trans["ps"] != "training mode":
            pass
    conn.close()
    #'''

def check_match(texts):
    # compare ps to text or g
    if texts["ps"] == texts["g"]:
        return 100

    else:
        return 0

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

def timestamp():
    return time.strftime("%Y%m%d_%H%M%S%Z")

def understand(trans, recog, audio):
    WIT_AI_KEY = "EOQY37HEGQHNKJ7M7IZMLVPETSDPF7QC" # Wit.ai keys are 32-character uppercase alphanumeric strings

    # recognize speech using PocketSphinx
    try:
        trans["ps"] = recog.recognize_sphinx(audio)
        print("Sphinx heard " + trans["ps"])

    except sr.UnknownValueError:
        print("Sphinx didn't understand anything you said...")

    except sr.RequestError as e:
        print("Sphinx error; {0}".format(e))

    # recognize speech using Wit.ai
    try:
        trans["wit"] = recog.recognize_wit(audio, key=WIT_AI_KEY)
        print("Wit.ai heard " + trans["wit"])

    except sr.UnknownValueError:
        print("Wit.ai didn't understand anything you said...")

    except sr.RequestError as e:
        print("Could not request results from Wit.ai service; {0}".format(e))

    if trans["ps"] == trans["wit"] or len(trans["wit"].split()) < 4:
        # don't use gsr
        print("Not using Google and totally ignoring this one.")
        trans["text"] = "ignore"

    else:
        # recognize speech using Google Speech Recognition
        try:
            # for testing purposes, we're just using the default API key
            # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
            # instead of `r.recognize_google(audio)`
            trans["g"] = recog.recognize_google(audio)
            print("Google heard " + trans["g"])

        except sr.UnknownValueError:
            print("Google didn't understand anything you said...")

        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
    answer(trans)
    sys.exit(0)  # just in case answer() doesn't exit for us

def answer(trans):
    conn = sqlite3.connect("memory/mem.db")

    if trans["ps"] == "reload" or trans["g"] == "reload" or trans["wit"] == "reload":
        return "reload"

    if trans["text"] == "ignore":
        # ignore triffles
        return "continue"
    match = check_match(trans)

    with open("memory/rec_" + trans["time"] + ".wav", "wb") as f:
        f.write(audio.get_wav_data())

    c = conn.cursor()

    try:
        # Ensure the target table exists
        c.execute("SELECT * FROM Ears ORDER BY time")

    except sqlite3.Error as e:

        if e.args[0] == "no such table: Ears":
            c.execute("CREATE TABLE Ears (time, ps_trans, g_trans, wit_trans, ibm_trans, att_trans, text, match)")

        else:
            print("Error:", e.args[0])
    entry = (trans["time"], trans["ps"], trans["g"], "", "", "", trans["text"], match)
    c.execute("INSERT INTO Ears VALUES (?, ?, ?, ?, ?, ?, ?, ?)", entry)
    conn.commit()
    c.close()

    if mode == "lrn" and trans["ps"] != "training mode":
        pass
    conn.close()
    sys.exit(0)

def speak_out(text, voice='slt', echo=True):
    # TTS via mimic
    run('mimic -voice ' + voice + ' "' + text + '" speech.wav')
    run('amarok speech.wav')
    run('rm speech.wav')

    if echo:
        print(text)

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
