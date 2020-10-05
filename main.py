import eel
from s60c import S60C

import logging
logging.basicConfig(level=logging.DEBUG)

@eel.expose
def start_fade(ipaddr, fades):
    node = S60C(ipaddr)
    # fades : [{duration:(ms), intensity:(percentage), temperature(K)}, ...]
    for d in fades:
        node.add_fade(d["intensity"], d["temperature"], d["duration"])
    
    node.start_fade()

eel.init('web')
eel.start('index.html', port=8080)