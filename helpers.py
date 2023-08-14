import ulid

def getULID():
    ulid_ref = ulid.new()
    return ulid_ref.str