import eel
import s60c

import argparse
argparser = argparse.ArgumentParser()
argparser.add_argument('-D', '--debug', action='store_true')
if argparser.parse_args().debug:
    import logging
    logging.basicConfig(level=logging.DEBUG)

node = None

@eel.expose
def start_fade(ipaddr, fades):
    global node
    def start():
        node = s60c.S60C(ipaddr)
        # fades : [{duration:(ms), intensity:(percentage), temperature(K)}, ...]
        for d in fades:
            node.add_fade(d["intensity"], d["temperature"], d["duration"])
        node.start_fade(eel.progress_callback, eel.finish_callback)
    start()

@eel.expose
def stop_fade():
    global node
    if not node is None:
        node.stop_fade()

eel.init('web')
eel.start('index.html', port=8080)