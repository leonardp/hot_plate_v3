class HP4067:
    def __init__( self, en, s0, s1, s2, s3 ):
        self.pin_en = en
        self.pin_s0 = s0
        self.pin_s1 = s1
        self.pin_s2 = s2
        self.pin_s3 = s3

    def enable(self):
        return self.pin_en.value(1)

    def disable(self):
        return self.pin_en.value(0)
        
    def set_channel(self, ch):
        self.pin_s0.value(ch >> 0 & 1)
        self.pin_s1.value(ch >> 1 & 1)
        self.pin_s2.value(ch >> 2 & 1)
        self.pin_s3.value(ch >> 3 & 1)
