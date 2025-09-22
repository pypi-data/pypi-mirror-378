# ----- type convert -----

# functions

def dataToBytes(data: str | bytes | tuple[str] | tuple[bytes]):
    if type(data) is tuple:
        result = tuple(dataToBytes(d) for d in data)
    elif type(data) is str:
        result = data.encode()
    else:
        result = data
    return result
