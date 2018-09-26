from machine import Pin as MachinePin


# noinspection PyUnresolvedReferences,PyArgumentList
class PinWrapper(MachinePin):
    def __init__(self,
                 key: int,
                 active: int,
                 id: int,
                 mode: int = -1
                 ):
        super().__init__(id, mode)
        self.key = key
        self.active = active
        self.gpio = id
        self.timer = None

    def on(self):
        super().value(self.active)

    def off(self):
        super().value(not self.active)

    def toggle(self):
        super().value(not super().value())

    def state(self):
        return super().value() == self.active

    def trigger(self, callback):
        if self.active == 1:
            super().irq(handler=callback, trigger=MachinePin.IRQ_RISING)
        else:
            super().irq(handler=callback, trigger=MachinePin.IRQ_FALLING)

    def debounce(self, period, callback):
        super().irq(handler=None)
        from machine import Timer
        self.timer = Timer(-1)
        self.timer.init(mode=Timer.ONE_SHOT, period=period, callback=callback)
