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
                LinearFadeMultiCore(S60C.perc2byte(intensity/100)).get_fades(),
                LinearFadeMultiCore(S60C.temp2byte(temperature)).get_fades(),
                duration_ms
            ]
        )

    def start_fade(self):
        async def fetch(q):
            while not q.empty():
                f = await q.get()
                self.intensity_channel.add_fade(f[0], f[2])
                self.temperature_channel.add_fade(f[1], f[2])
                await self.intensity_channel.wait_till_fade_complete()
            await self.node.stop()
        
        asyncio.get_event_loop().run_until_complete(fetch(self.queue))
        print("FIN")

    def terminate(self):
        self.node = None
        self.univ = None

    def temp2byte(temprature):
        p = (temprature - TEMP_LOWER) / TEMP_WIDTH
        return S60C.perc2byte(p)

    def perc2byte(percentage):
        return int(percentage * 65535).to_bytes(2, 'big')

    def byte2temp(tempbytes):
        return float(int.from_bytes(tempbytes)) / 65535 * TEMP_WIDTH + TEMP_LOWER

    def byte2perc(percbytes):
        return float(int.from_bytes(percbytes)) / 655.35
