# ----- test -----

# imports

from pwntools_util import PwnUtil
from pwntools_util.util.text_colors import colorize, TextColorCodes

# test

def test_client():
    print(f"[{colorize('pwntools_util', TextColorCodes.Blue)}]: Testing pwntools util...")

    # Connect
    ppp = PwnUtil()
    ppp.connectLocal_py("./tests/test_server.py")

    # Get data
    print(ppp.getline().strip().decode())
    print(ppp.getFromLine_Int())
    print(ppp.getFromLine_Float())
    print(ppp.getAllFromLine_Int())
    print(ppp.getListFromLine_Int())
    print(ppp.getListFromLine_Float())
    print(int(ppp.getline().split()[-1], 16))

    # Send data
    ppp.getuntil("-> ")
    ppp.sendline(colorize('I <3 pwnUtil', TextColorCodes.Green))
    print(ppp.getline().strip().decode())

    # Disconnect
    ppp.disconnect()
