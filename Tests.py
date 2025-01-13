from pyftdi.ftdi import Ftdi
import pyftdi.serialext
import pluggy
import inspect


class tester:

    hookimpl = pluggy.HookimplMarker("pyIVLS")

    @hookimpl
    def imma_hook(self):
        print("Hookin'")

    def get_a_load(self):
        print("griftin'")

    def of_this_guy(self):
        print("griftin' people")


if __name__ == "__main__":
    t = tester()

    methods_list = [
        method[0] for method in inspect.getmembers(t, predicate=inspect.ismethod)
    ]

    print(methods_list)

import time
import pyvisa

def KeithleyRunDualChSweep(s):
    waitDelay = float(s['pulse']) if s['pulse'] != 'off' else 1

    self.safewrite(f"{s['source']}.nvbuffer1.clear()")
    self.safewrite(f"{s['source']}.nvbuffer2.clear()")
    self.safewrite(f"{s['drain']}.nvbuffer1.clear()")
    self.safewrite(f"{s['drain']}.nvbuffer2.clear()")
    self.safewrite(f"{s['source']}.trigger.count = {s['steps']}")
    self.safewrite(f"{s['source']}.trigger.arm.count = {s['repeat']}")
    self.safewrite(f"{s['drain']}.trigger.count = {s['steps']}")
    self.safewrite(f"{s['drain']}.trigger.arm.count = {s['repeat']}")
    self.safewrite(f"display.{s['drain']}.measure.func = display.MEASURE_DCAMPS")
    self.safewrite(f"{s['source']}.trigger.source.linear{s['type']}({s['start']},{s['end']},{s['steps']})")

    if s['type'] == 'i':
        if s['pulse'] == 'off' or (abs(s['start']) < 1.5 and abs(s['end']) < 1.5):
            self.safewrite(f"{s['source']}.trigger.source.limitv = {s['limit']}")
            self.safewrite(f"{s['source']}.source.limitv = {s['limit']}")
        else:
            self.safewrite("smua.measure.filter.enable = smua.FILTER_OFF")
            self.safewrite("smub.measure.filter.enable = smub.FILTER_OFF")
            self.safewrite(f"{s['source']}.source.autorangei = {s['source']}.AUTORANGE_OFF")
            self.safewrite(f"{s['source']}.source.autorangev = {s['source']}.AUTORANGE_OFF")
            self.safewrite(f"{s['drain']}.source.autorangei = {s['drain']}.AUTORANGE_OFF")
            self.safewrite(f"{s['drain']}.source.autorangev = {s['drain']}.AUTORANGE_OFF")
            self.safewrite(f"{s['source']}.measure.rangei = 10")
            self.safewrite(f"{s['drain']}.measure.rangei = 10")
            self.safewrite(f"{s['source']}.source.delay = 100e-6")
            self.safewrite(f"{s['source']}.measure.autozero = {s['source']}.AUTOZERO_OFF")
            self.safewrite(f"{s['source']}.source.rangei = 10")
            self.safewrite(f"{s['source']}.source.leveli = 0")
            self.safewrite(f"{s['source']}.source.limitv = 6")
            self.safewrite(f"{s['source']}.trigger.source.limiti = 10")
        self.safewrite(f"display.{s['source']}.measure.func = display.MEASURE_DCVOLTS")
    else:
        if s['pulse'] == 'off' or abs(s['limit']) < 1.5:
            self.safewrite(f"{s['source']}.trigger.source.limiti = {s['limit']}")
            self.safewrite(f"{s['source']}.source.limiti = {s['limit']}")
        else:
            self.safewrite("smua.measure.filter.enable = smua.FILTER_OFF")
            self.safewrite("smub.measure.filter.enable = smub.FILTER_OFF")
            self.safewrite(f"{s['source']}.source.autorangei = {s['source']}.AUTORANGE_OFF")
            self.safewrite(f"{s['source']}.source.autorangev = {s['source']}.AUTORANGE_OFF")
            self.safewrite(f"{s['drain']}.source.autorangei = {s['drain']}.AUTORANGE_OFF")
            self.safewrite(f"{s['drain']}.source.autorangev = {s['drain']}.AUTORANGE_OFF")
            self.safewrite(f"{s['source']}.measure.rangei = 10")
            self.safewrite(f"{s['drain']}.measure.rangei = 10")
            self.safewrite(f"{s['source']}.source.delay = 100e-6")
            self.safewrite(f"{s['source']}.measure.autozero = {s['source']}.AUTOZERO_OFF")
            self.safewrite(f"{s['source']}.source.rangev = 6")
            self.safewrite(f"{s['source']}.source.levelv = 0")
            self.safewrite(f"{s['source']}.source.limiti = 0.1")
            self.safewrite(f"{s['source']}.trigger.source.limiti = 10")
        self.safewrite(f"display.{s['source']}.measure.func = display.MEASURE_DCAMPS")

    if s['drainVoltage'] != 'off':
        self.safewrite(f"{s['drain']}.source.func = {s['drain']}.OUTPUT_DCVOLTS")
        self.safewrite(f"{s['drain']}.source.levelv = {s['drainVoltage']}")
        self.safewrite(f"{s['drain']}.source.limiti = {s['drainLimit']}")
        drainLimitVoltage = float(s['drainLimit'])
    else:
        self.safewrite(f"{s['drain']}.source.func = {s['drain']}.OUTPUT_DCVOLTS")
        self.safewrite(f"{s['drain']}.source.levelv = 0")
        if s['type'] == 'v' and s['limit'] > 1.5:
            self.safewrite(f"{s['drain']}.source.limiti = 1.5")
            drainLimitVoltage = 1.5
        else:
            self.safewrite(f"{s['drain']}.source.limiti = {s['limit']}")
            drainLimitVoltage = s['limit']
        if s['type'] == 'i':
            self.safewrite(f"{s['drain']}.source.limiti = {s['end']}")
            drainLimitVoltage = s['end']

    self.safewrite(f"{s['source']}.source.output = {s['source']}.OUTPUT_ON")
    self.safewrite(f"{s['drain']}.source.output = {s['drain']}.OUTPUT_ON")
    self.safewrite(f"{s['drain']}.trigger.initiate()")
    self.safewrite(f"{s['source']}.trigger.initiate()")
    time.sleep(waitDelay)