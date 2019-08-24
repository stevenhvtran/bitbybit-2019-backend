from server import credentials
import pyrebase


def get_db():
    firebase = pyrebase.initialize_app(credentials.get_credentials())
    return firebase.database()
