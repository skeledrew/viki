def voice(params={}):
    print('dbg: callback')

    if not params:
        # return settings if no params
        return {'engines': ['use_ps', 'use_wit', 'use_ggl']}

    if not params['ps'] == '':
        print('PocketSphinx heard: ' + params['ps'])

    if not params['wit'] == '':
        print('Wit.ai heard: ' + params['wit'])

    if not params['ggl'] == '':
        print('Google heard: ' + params['ggl'])

    if not params['hnd'] == '':
        print('Houndify heard: ' + params['hnd'])

    if not params['bng'] == '':
        print('Bing heard: ' + params['bng'])

    if not params['ibm'] == '':
        print('IBM heard: ' + params['ibm'])

def recog_test():
    pass

if __name__ == '__main__':
    import importlib
    voice = importlib.import_module('voice')
    print('Recognize a single occurence')
    print(voice.stt())  # needs work
    print('Recognition complete')

else:
    #print('import successful!')
    pass
