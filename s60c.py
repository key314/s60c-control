import async_eel
from pyartnet import ArtNetNode
from LinearFadeMulti import LinearFadeMultiCore
import asyncio
import time

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
        self.__is_running = False

    def add_fade(self, intensity, temperature, duration_ms):
        self.queue.put_nowait(
            [
                LinearFadeMultiCore(S60C.perc2byte(intensity/100)),
                LinearFadeMultiCore(S60C.temp2byte(temperature)),
                duration_ms
            ]
        )

    def start_fade(self, progress_callback, fade_finished_callback):
        async def count_progress(wait_sec):
            end_time = time.time() + wait_sec
            interval = wait_sec / 100
            if interval < 0.1:
                interval = 0.1
            while self.__is_running:
                remain = end_time - time.time()
                progress_callback(100 - (remain / wait_sec * 100))
                if remain < interval:
                    return True
                await asyncio.sleep(interval)
            return False

        async def fetch():
            task_id = 0
            while not self.queue.empty():
                q = await self.queue.get()
                self.intensity_channel.add_fade(q[0].get_fades(), q[2])
                self.temperature_channel.add_fade(q[1].get_fades(), q[2])
                is_finished = await count_progress(q[2] / 1000)
                await self.intensity_channel.wait_till_fade_complete()
                await self.temperature_channel.wait_till_fade_complete()
                if is_finished:
                    fade_finished_callback(task_id)
                task_id += 1
            await self.node.stop()
            self.__is_running = False
        
        self.__is_running = True
        asyncio.run_coroutine_threadsafe(fetch(), asyncio.get_event_loop())
        #asyncio.get_event_loop().run_until_complete(fetch())

    def stop_fade(self):
        while not self.queue.empty():
            self.queue.get_nowait()
        self.intensity_channel.cancel_fades()
        self.temperature_channel.cancel_fades()
        self.__is_running = False

    def temp2byte(temprature):
        p = (temprature - TEMP_LOWER) / TEMP_WIDTH
        return S60C.perc2byte(p)

    def perc2byte(percentage):
        return int(percentage * 65535).to_bytes(2, 'big')

    def prog2temp(progress):
        return (progress * TEMP_WIDTH) + TEMP_LOWER