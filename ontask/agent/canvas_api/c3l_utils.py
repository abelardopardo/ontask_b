import datetime
import hashlib
import random as rd

def get_unique_key():
    return hashlib.md5((str(datetime.datetime.now().timestamp()) + str(rd.randint(1, 10000000))).encode('ascii')).hexdigest()