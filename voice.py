#! /usr/bin/python3


import speech_recognition as sr
import sqlite3
import os
import sys
from subprocess import call as run
from viki_utils import *
from multiprocessing import Process, Lock, Queue, Manager
from multiprocessing.connection import wait
import importlib


def stt(params={}):
    # use when calling as a module
    s_mem, o_mem = init(params)
    '''proc = Process(target=listen, args=((s_mem, o_mem)))
    print('dbg:', proc)
    proc.start()
    sentinel = []
    sentinel = sentinel.append(proc.sentinel())

    while sentinel:

        if wait(sentinel):
            sentinel = None'''
    proc = Process(target=listen, args=((s_mem, o_mem))).start()

    while o_mem['mainq'].empty():
        sleep(0.1)
    o_mem['llock'].acquire()

    while not o_mem['mainq'].empty():
        itm = None

        try:
            itm = o_mem['mainq'].get()

            if itm[0] == 'trans':
                o_mem['llock'].release()
                return itm[1]

        except:
            pass

def lual(params={}):
    s_mem, o_mem = init(params)

    while True:

        if not s_mem['listening']:
            # ensure a listener is running
            s_mem['listening'] = True
            proc = Process(target=listen, args=((s_mem, o_mem))).start()
        msg = None
        o_mem['llock'].acquire()

        if o_mem['mainq'].empty():
            # TODO: convert to sentinel method
            o_mem['llock'].release()
            sleep(0.1)
            continue
        '''proc = Process(target=listen, args=((s_mem, )))
        proc.start()
        sentinel = [].append(proc.sentinel())

        while sentinel:

            if wait(sentinel):
                sentinel = None'''
        msg = {}

        while not o_mem['mainq'].empty():
            # rebuild s_mem
            itm = None

            try:
                itm = o_mem['mainq'].get()
                msg[itm[0]] = itm[1]

            except Exception as e:
                print('error: mq get', itm, e)
                pass
        o_mem['llock'].release()
        s_mem = msg
        action = s_mem['action']

        if s_mem['trans']['ps'] == '':
            sleep(0.2)
            continue

        if action == 'exit':
            # kill children first?
            print('Goodbye cruel world :\'-(')
            break

        if action == 'reload':

            try:
                importlib.reload(o_mem['cmd_mod'])
                o_mem['callback'] = getattr(o_mem['cmd_mod'], s_mem['cb_name'])
                print('Reloaded commands module!')

            except Exception as e:
                print('No module to reload...', e)

        if action == 'delegate':

            try:
                # run external commands in another process
                Process(target=o_mem['callback'], args=((s_mem['trans'], ))).start()

            except Exception as e:
                print('Error: delegation failed ', e)


def init(params={}):
    s_mem = {}  # short term memory; make it easier to pass stuff around
    o_mem = {}  # object memory; use to pass esp process-related objects

    if not os.path.exists('memory'):
        # ensure the memory folder exists
        os.makedirs('memory')
    o_mem['conn'] = sqlite3.connect("memory/mem.db")
    s_mem['tokens'] = get_tokens()
    s_mem['mode'] = "cmd"  # lrn, dct, prg
    #wav_pos = ""
    o_mem['llock'] = Manager().Lock()  # listen lock
    o_mem['mlock'] = Manager().Lock()  # memory lock
    o_mem['mainq'] = Manager().Queue()  # main queue
    s_mem['listening'] = False
    #s_mem['listener'] = None
    s_mem['action'] = None

    if params:
        # can be used to override some defaults

        for key in params:

            if key in ['callback', 'cmd_mod']:
                # separate objects
                o_mem[key] = params[key]

            else:
                s_mem[key] = params[key]
    return s_mem, o_mem

def listen(s_mem, o_mem):
    print('dbg: enter listen')
    s_mem['recog'] = sr.Recognizer()
    s_mem['audio'] = None
    tstamp = '00'
    c_lock = Manager().Lock()  # clone lock
    c_queue = Manager().Queue()  # clone queue
    s_mem['trans'] = {"time" : "00", "ps" : "", "ggl" : "", "wit" : "", "ibm" : "", "att" : "", "text" : "", "wavs" : ''}

    with sr.Microphone() as source:
        s_mem['listening'] = True
        print('Now listening...')
        s_mem['audio'] = s_mem['recog'].listen(source)
        print('Sending audio for processing!')
        s_mem['trans']['time'] = timestamp()
    s_mem['listening'] = False
    o_mem['llock'].acquire()

    for itm in s_mem:
        # break down s_mem to partially avoid 'Unserializable message' error
        try:
            o_mem['mainq'].put([itm, s_mem[itm]])

        except Exception as e:
            print('error: mq put', [itm, s_mem[itm]], e.args[0])
            pass
    o_mem['llock'].release()
    c_queue.put(0)
    Process(target=understand, args=((s_mem, o_mem, 'default', c_queue))).start()
    print('dbg: exit listen')
    sys.exit(0)

def understand(s_mem, o_mem, action='default', clone=None):
    trans = s_mem['trans']
    recog = s_mem['recog']
    audio = s_mem['audio']

    if action == 'default':
        print('dbg: enter understand')

        clones = clone.get()
        #print('dbg: clone count', clones)
        #clone.put(clones+1)
        sentinels = []
        engines = ['use_ps']
        o_mem['subq'] = Queue()

        for engine in engines:
            # parallel recognition
            proc = Process(target=understand, args=((s_mem, o_mem, engine)))
            proc.start()
            sentinels.append(proc.sentinel)

        while sentinels:

            for sentinel in wait(sentinels):
                # remove ready (terminated) processes and check results queue
                sentinels.remove(sentinel)
                msg = o_mem['subq'].get()
                s_mem['trans'][msg[0]] = msg[1]

        Process(target=remember, args=((s_mem, o_mem))).start()
        print('dbg: exit understand')
        answer(s_mem, o_mem)
        sys.exit(0)
        return

    if action == 'use_ps':
        # recognize speech using PocketSphinx

        try:
            text = recog.recognize_sphinx(audio)
            print('PocketSphinx heard ' + text)
            o_mem['subq'].put(['ps', text])
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
            print('Wit.ai heard ' + text)
            o_mem['subq'].put(['wit', text])
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
            #print('Google heard ' + text)
            o_mem['subq'].put(['ggl', text])
            return

        except sr.UnknownValueError:
            print("Google didn't understand anything you said...")

        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
    print('Error: Invalid action passed')

def remember(s_mem, o_mem):
    o_mem['mlock'].acquire()
    conn = o_mem['conn']
    trans = s_mem['trans']

    if len(trans["wit"].split(' ')) < 4:
        # ignore small utterances
        o_mem['mlock'].release()
        sys.exit(0)
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
    o_mem['mlock'].release()
    sys.exit(0)

def answer(s_mem, o_mem={}):
    print('dbg: enter answer')
    trans = s_mem['trans']

    if trans["wit"] == "reload" or trans["ps"] == "reload" or trans["ggl"] == "reload":
        s_mem['action'] = 'reload'

    elif trans["wit"] == "goodbye" or trans["ps"] == "goodbye" or trans["ggl"] == "goodbye":
        s_mem['action'] = 'exit'

    else:
        s_mem['action'] = 'delegate'
    o_mem['llock'].acquire()

    for itm in s_mem:

        try:
            o_mem['mainq'].put([itm, s_mem[itm]])

        except Exception as e:
            print('error: mq put', [itm, s_mem[itm]], e.args[0])
            pass
    o_mem['llock'].release()
    print('dbg: exit answer')
    sys.exit(0)

def next_train_wav(cnt=0):
    # find next available file name in the series
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

def run_method(mod, meth, args=[]):
    return getattr(mod, meth)(args)

def main(args):

    if len(args) == 1:
        lual()
        return
    curr_name = args[0]

    if os.path.isfile(args[1]):
        # get callback method from commands script
        try:
            arg_mod = importlib.import_module(args[1].split('.')[0])
            meth_name = args[0].split('/')[-1].split('.')[0]  # DEBUG: will break on Windows!!
            #print(run_method(arg_mod, meth_name, ['my args received!!!']))
            lual({'cb_name': meth_name, 'callback': getattr(arg_mod, meth_name), 'cmd_mod': arg_mod})

        except:
            print('Argument must be a Python script "name.ext" with a method called "' + args[0].split('/')[-1].split('.')[0] + '"')


if __name__ == '__main__':
    main(sys.argv)
