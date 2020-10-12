from pyartnet.fades.fade_base import FadeBase

class LinearFadeMulti(FadeBase):
    def __init__(self, target : int, core, byte_pos : int):
        super().__init__(target)
        self.pos = byte_pos
        self.core = core

    def initialize_fade(self, steps: int):
        self.core.initialize_fade(steps, self.pos)

    def calc_next_value(self):
        self.val_current = self.core.calc_next_value(self.pos)
    
    def is_done(self):
        return self.core.is_done()

class LinearFadeMultiCore:
    def __init__(self, target : list):
        width = len(target)

        self.__val_start : float = 0
        self.__val_target : float = 0
        self.__val_current : float = 0.0
        self.__factor : float = 1.0
        self.__flag = [False] * width

        self.__fades = [LinearFadeMulti(target[i], self, i) for i in range(width)]
    
    def get_fades(self):
        return self.__fades

    def initialize_fade(self, steps : int, pos):
        if not self.__flag[pos]:
            self.__flag[pos] = True
        if self.__flag.count(False) == 0:
            self.__val_start = 0
            self.__val_target = 0
            for i, v in enumerate(self.__fades):
                self.__val_start += v.val_start << ((len(self.__fades) - i - 1) * 8)
                self.__val_target += v.val_target << ((len(self.__fades) - i - 1) * 8)
            self.__val_current = float(self.__val_start)
            self.__factor = (self.__val_target - self.__val_start) / steps

    def calc_next_value(self, pos):
        if self.__flag[pos]:
            for i in range(len(self.__flag)):
                self.__flag[i] = i == pos
            self.__val_current += self.__factor
        else:
            self.__flag[pos] = True

        return int(self.__val_current) >> ((len(self.__fades) - pos - 1) * 8) & 0xff

    def get_progress(self):
        return (self.__val_current - self.__val_start) / (self.__val_target - self.__val_start)

    def is_done(self):
        curr = round(self.__val_current)
        if (self.__factor <= 0 and curr <= self.__val_target) or \
            (self.__factor >= 0 and curr >= self.__val_target):
            if self.__flag.count(False) == 0:
                return True
        
        return False