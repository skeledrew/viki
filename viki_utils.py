import time


def check_match(texts):
    # compare ps to text or g
    if texts["ps"] == texts["g"]:
        return 100

    else:
        return 0

def timestamp():
    return time.strftime("%Y%m%d_%H%M%S%Z")

def get_tokens():
    # get any tokens from the file 'tokens'; file not to be committed
    tokens = {}

    with open('tokens') as f:

        for line in f:
            token = line.split(' ')
            tokens[token[0]] = token[1]
    return tokens

