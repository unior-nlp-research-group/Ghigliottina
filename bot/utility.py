
def flatten(L):
    ret = []
    for i in L:
        if isinstance(i,list):
            ret.extend(flatten(i))
        else:
            ret.append(i)
    return ret

def represents_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def represents_int_between(s, low, high):
    if not represents_int(s):
        return False
    sInt = int(s)
    if sInt>=low and sInt<=high:
        return True
    return False

MARKDOWN_CHARS = '*_`['

def contains_markdown(text):
    return any(c in text for c in MARKDOWN_CHARS)

def escape_markdown(text):
    for char in MARKDOWN_CHARS:
        text = text.replace(char, '\\'+char)
    return text

def remove_markdown(text):
    for char in MARKDOWN_CHARS:
        text = text.replace(char, '')
    return text

def get_now_seconds():
    import time
    # returns Milliseconds since the epoch
    return int(round(time.time()))
