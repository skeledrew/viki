def voice(params={}):
    print('method accessed!!')
    print(params)
    return 'returned stuff!!!!'

def recog_test():
    pass

if __name__ == '__main__':
    import importlib
    voice = importlib.import_module('voice')
    print('Recognize a single occurence')
    print(voice.stt())
    print('Recognition complete')

else:
    print('import successful!')
