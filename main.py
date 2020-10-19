import async_eel
import s60c
import asyncio
import logging

import argparse
argparser = argparse.ArgumentParser()
argparser.add_argument('-D', '--debug', action='store_true')
if argparser.parse_args().debug:
    logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

loop = asyncio.get_event_loop()
node = None

@async_eel.expose
async def start_fade(ipaddr, fades):
    log.debug('start_fade() is called.')
    global node
    node = s60c.S60C(ipaddr)
    # fades : [{duration:(ms), intensity:(percentage), temperature(K)}, ...]
    for d in fades:
        node.add_fade(d["intensity"], d["temperature"], d["duration"])
    async_eel.spawn(node.start_fade, async_eel.progress_callback, async_eel.finish_callback)

@async_eel.expose
def stop_fade():
    log.debug('stop_fade() is called.')
    global node
    if not node is None:
        node.stop_fade()
        node = None
    else:
        log.debug('node is None.')

async def main():
    async_eel.init('web')
    await async_eel.start('index.html', port=8080)

if __name__ == '__main__':
    try:
        asyncio.run_coroutine_threadsafe(main(), loop)
        loop.run_forever()
    except (SystemExit, MemoryError, KeyboardInterrupt):
        stop_fade()
    