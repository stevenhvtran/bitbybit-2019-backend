import os


def get_credentials():
    apiKey = os.environ['apiKey']
    authDomain = os.environ['authDomain']
    databaseURL = os.environ['databaseURL']
    storageBucket = os.environ['storageBucket']
    return {
        "apiKey": apiKey,
        "authDomain": authDomain,
        "databaseURL": databaseURL,
        "storageBucket": storageBucket
    }
