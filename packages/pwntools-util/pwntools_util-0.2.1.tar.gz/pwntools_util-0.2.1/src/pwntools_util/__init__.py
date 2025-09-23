# pwntools wrapper with bytes casting and common utils

# ----- pwn -----

# imports

from .util import string_getter, type_convert
from .util.text_colors import colorize, TextColorCodes

import pwn

# class

class PwnUtil:
    def __init__(self):
        self._conn = None
        self._header = f"[{colorize('PwnUtil', TextColorCodes.Yellow)}]"

    # Connect / disconnect

    def connectRemote(self, host: str, port: int,
                      fam = "any", typ = "tcp",
                      sock=None, ssl=False, ssl_context=None, ssl_args=None, sni=True,
                      *args, **kwargs):
        print(f"{self._header}: Connecting to {colorize('remote', TextColorCodes.Green)}!")
        self._conn = pwn.remote(host, port, fam, typ, sock, ssl, ssl_context, ssl_args, sni, *args, **kwargs)

    def connectLocal(self, argv = None, *args, **kwargs):
        print(f"{self._header}: Connecting to {colorize('local', TextColorCodes.Blue)}!")
        self._conn = pwn.process(argv, *args, **kwargs)

    def disconnect(self):
        if self._conn:
            self._conn.close()
            print(f"{self._header}: Disconnected!")

    # Get & send

    def getline(self, timeout = 5):
        return self._conn.recvline(timeout=timeout)

    def getuntil(self, data: str | bytes | tuple[str] | tuple[bytes], timeout = 5):
        return self._conn.recvuntil(type_convert.dataToBytes(data), timeout=timeout)

    def getall(self, timeout = 5):
        return self._conn.recvall(timeout=timeout)

    def sendline(self, data: str | bytes):
        self._conn.sendline(type_convert.dataToBytes(data))

    def interactive(self):
        self._conn.interactive()

    # Utility

    def getFromLine_Int(self):
        return string_getter.getFromString_Int(self.getline().decode())

    def getAllFromLine_Int(self):
        return string_getter.getAllFromString_Int(self.getline().decode())

    def getListFromLine_Int(self):
        return string_getter.getListFromString_Int(self.getline().decode())
    
    def getFromLine_Float(self):
        return string_getter.getFromString_Float(self.getline().decode())

    def getAllFromLine_Float(self):
        return string_getter.getAllFromString_Float(self.getline().decode())

    def getListFromLine_Float(self):
        return string_getter.getListFromString_Float(self.getline().decode())
