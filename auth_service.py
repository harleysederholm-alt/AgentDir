import datetime

def create_token():
    # VIRHE: Käyttää paikallista aikaa
    return {"issued_at": datetime.datetime.now()}
