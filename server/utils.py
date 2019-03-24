import re
def checkpw(password):
    pattern = r'^(?=.*[a-zA-z])(?=.*[0-9])(?=.{6,})'
    return not not re.search(pattern, password)