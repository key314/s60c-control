from pyartnet import ArtNetNode
from LinearFadeMulti import LinearFadeMultiCore
import asyncio

TEMP_LOWER = 2800.0
TEMP_WIDTH = 10000.0 - TEMP_LOWER

class S60C:
    def __init__(self, ipaddr):
        self.node = ArtNetNode(ipaddr)
        self.node.start()
        univ = self.node.add_universe(0)
        self.intensity_channel = univ.add_channel(1, 2)
        self.temperature_channel = univ.add_channel(3, 2)
        self.queue = asyncio.Queue()

    def add_fade(self, intensity, temperature, duration_ms):
        self.queue.put_nowait(
            [
                LinearFadeMultiCore(S60C.perc2byte(intensity/100)),
                LinearFadeMultiCore(S60C.temp2byte(temperature)),
                duration_ms
            ]
        )

    def start_fade(self, change_callback, fade_finished_callback):
        async def fetch():
            i = 0
            while not self.queue.empty():
                q = await self.queue.get()
                self.intensity_channel.add_fade(q[0].get_fades(), q[2])
                self.intensity_channel.callback_value_changed = \
                    lambda: change_callback(q[0].get_progress() * 100)
                self.temperature_channel.add_fade(q[1].get_fades(), q[2])
                await self.intensity_channel.wait_till_fade_complete()
                await self.temperature_channel.wait_till_fade_complete()
                fade_finished_callback(i)
                i += 1
            await self.node.stop()
        
        asyncio.get_event_loop().run_until_complete(fetch())

    def terminate(self):
        self.node = None
        self.univ = None

    def temp2byte(temprature):
        p = (temprature - TEMP_LOWER) / TEMP_WIDTH
        return S60C.perc2byte(p)

    def perc2byte(percentage):
        return int(percentage * 65535).to_bytes(2, 'big')

    def prog2temp(progress):
        return (progress * TEMP_WIDTH) + TEMP_LOWER